import argparse
import os
import sys
import shutil
import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
import subprocess
from tqdm.auto import tqdm


def update_progress(task_id, processed_count, basePath):
    sys.path.append(basePath)
    from nb_app.models import DockingProgress
    progress = DockingProgress.objects.get(task_id=task_id)
    progress.processed_ligands = processed_count
    progress.save()

def create_config(basePath, ligand_name, receptor_name):
    utilities_path = Path(basePath) / 'utilities' / 'docking'
    base_config_path = utilities_path / 'config_files' / 'config_vina.txt'
    ligand_path = utilities_path / 'undocked_ligands' / f'{ligand_name}.pdbqt'
    receptor_path = utilities_path / 'cleaned_receptors' / f'{receptor_name}.pdbqt'
    config_dir = utilities_path / 'config_files'
    
    new_config_path = config_dir / f'config_run_{ligand_name}.txt'
    with open(base_config_path, 'r') as base_config, open(new_config_path, 'w') as new_config:
        for line in base_config:
            line = line.replace('$ligand', str(ligand_path)).replace('$receptor', str(receptor_path))
            new_config.write(line)
    return new_config_path

def prepare_ligand(basePath, ligand_path, output_path):


    # Define base path to MGLTools
    mgltools_path = Path(basePath) / 'utilities' / 'docking' / 'Tools' / 'MGLTools-1.5.7'
    python_mgl_exe_path = mgltools_path / 'python_mgl.exe'

    # Define path to the prepare_ligand4.py script
    prepare_ligand4_script_path = mgltools_path / 'Lib' / 'site-packages' / 'AutoDockTools' / 'Utilities24' / 'prepare_ligand4.py'

    # Construct the command list
    cmd = [
        str(python_mgl_exe_path), str(prepare_ligand4_script_path),
        '-l', str(ligand_path),
        '-o', str(output_path),
        '-A', 'hydrogens'
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error preparing ligand {ligand_path.name}: {e}")
        return False
    return True

def smi_to_pdb(smi, output_path):
    mol = Chem.MolFromSmiles(smi)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)
    AllChem.MMFFOptimizeMolecule(mol)
    Chem.MolToPDBFile(mol, str(output_path))

def run_vina(config_path, ligand_name, basePath):
    vina_path = Path(basePath) / 'utilities' / 'docking' / 'Tools' / 'vina'
    log_path = config_path.with_suffix('.log')
    cmd = [str(vina_path), '--config', str(config_path), '--log', str(log_path)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Vina for ligand {ligand_name}: {e}")
        return False
    return True

def dock_ligand(ligand_name, receptor_name, basePath, idx, task_id):
    config_path = create_config(basePath, ligand_name, receptor_name)
    ligand_path = Path(basePath) / 'utilities' / 'docking' / 'undocked_ligands' / f'{ligand_name}.pdb'
    output_path = ligand_path.with_suffix('.pdbqt')
    
    if not prepare_ligand(basePath, ligand_path, output_path):
        return False
    
    if not run_vina(config_path, ligand_name, basePath):
        return False
    
    # Update progress
    update_progress(task_id, idx, basePath)
    return True

def main():
    parser = argparse.ArgumentParser(description='Run docking')
    parser.add_argument('--base_directory', type=str, required=True, help='Base directory of the project')
    parser.add_argument('--task_id', type=str, required=True, help='Unique task ID for progress tracking')
    args = parser.parse_args()

    # Load SMILES and IDs
    smi_file_path = Path(args.base_directory) / 'utilities' / 'docking' / 'dataset' / 'test2.csv'
    smi_df = pd.read_csv(smi_file_path)
    
    receptor_name = 'example_receptor'  # Replace with your receptor name
    
    for idx, row in tqdm(smi_df.iterrows(), total=smi_df.shape[0]):
        ligand_id = row['ChEMBL ID']
        smi = row['Smiles']
        ligand_path = Path(args.base_directory) / 'utilities' / 'docking' / 'undocked_ligands' / f'{ligand_id}.pdb'
        
        # Convert SMILES to PDB
        smi_to_pdb(smi, ligand_path)
        
        # Docking
        if not dock_ligand(ligand_id, receptor_name, args.base_directory, idx, args.task_id):
            print(f"Docking failed for {ligand_id}")

if __name__ == "__main__":
    main()
