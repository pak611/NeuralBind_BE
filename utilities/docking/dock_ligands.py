
try:
    from openbabel import pybel
except:
    import pybel
import pandas as pd
import argparse
from functools import partial
from multiprocessing import Pool
from tqdm.auto import tqdm
import os
from pathlib import Path
import rdkit
import pebble
from rdkit import Chem
from pebble import concurrent, ProcessPool
import shutil
import glob
#from concurrent.futures TimeoutError

import os
import sys





BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append('C:/Users/patri/Dropbox/Ph.D/OrganoNet/Websites/NeuralBind_FEBE/NeuralBind_BE')

# import DockingProgress model from your Django app's models.py file
#from nb_app.models import DockingProgress

def update_progress(task_id, processed_count):

    from nb_app.models import DockingProgress # import into function to avoid initialization issues
    progress = DockingProgress.objects.get(task_id=task_id)
    progress.processed_ligands = processed_count
    progress.save()

#1 convert smiles list to pdb files

#2 convert the ligand.pdb files to ligand.pdbqt

#2.5 create the configuration files

#3 run the docking -> ligand.pdbqt

def createConfig(filehandle, receptorFile, configFile, basePath):
    basePath = Path(basePath)

    baseConfig = basePath / 'utilities' / 'docking' / 'config_files' / f'config_vina.txt'

    ligand = basePath / 'utilities' / 'docking' / 'undocked_ligands' / f'{filehandle}.pdbqt'
    receptor = basePath / 'utilities' / 'docking' / 'cleaned_receptors' / f'{receptorFile}.pdbqt'

    # Create the new config file
    ligConfig = f'config_run_{ligand.stem}.txt'
    config_dir = basePath / 'utilities' / 'docking' / 'config_files'
    
    with baseConfig.open('r+') as openBaseConfig, config_dir.joinpath(ligConfig).open('w') as openConfig:
        for line in openBaseConfig:
            if '$ligand' in line:
                line = line.replace('$ligand', str(ligand))
            if '$receptor' in line:
                line = line.replace('$receptor', str(receptor))
            openConfig.write(line)


    return ligConfig




def prepLigand(filehandle,basePath):
    # change in AWS
    #----------
    prepare_ligand4 = 'C://Users/patri/Dropbox/Ph.D/Research/Doctoral_Research/Cheminformatics/IFP-RNN/MGLTools-1.5.7/python_mgl.exe C://Users/patri/Dropbox/Ph.D/Research/Doctoral_Research/Cheminformatics/IFP-RNN/MGLTools-1.5.7_old/Lib/site-packages/prepare_ligand4.py'
    #------------------

    pdbqtfile = f'{filehandle}.pdbqt'
    pdbfile = f'{filehandle}.pdb'
    pdbqtfilepath = Path(pdbqtfile)

 

    pdbfilepath = Path(f'{basePath}\\utilities\\docking\\undocked_ligands\\{pdbfile}')
    #pdbfilepath = 'C://Users/patri/Dropbox/Ph.D/OrganoNet/NeuralBind/docking/undocked_ligands/Codeine.pdb'
    cmd = f"{prepare_ligand4} -l {pdbfilepath} -o {pdbqtfilepath} -A hydrogens"
    #cmd = cmd.replace('\\', '/')


 
    os.chdir(f'{basePath}\\utilities\\docking\\undocked_ligands')

    

    try:
        os.system(cmd)
        os.chdir('..\\..\\..\\')
        print('ln 87')
        #os.system(f'del {pdbfilepath}')
        return 1
    except:
        print("file has been removed")
    return 0

def dockSingLig(filehandle, receptorFile, configFile, basePath, idx, task_id=None):


    #vinaPath = f'{args.mgltools}vina'
    vinaPath = Path(f'{basePath}\\utilities\\docking\\Tools\\MGLTools-1.5.7\\vina.exe') # path to vina dock executable
    # create the config file
    print(f'the filehandle is {filehandle}')

    ligConfig = Path(f'{basePath}\\utilities\\docking\\config_files\\{createConfig(filehandle, receptorFile=receptorFile, configFile=configFile, basePath=basePath)}')
    
    
    logFile = Path(f'{basePath}\\utilities\\docking\\config_files\\{configFile}_config\\{filehandle}_log.txt')
    cmd = f'{vinaPath} --config {ligConfig} --log {logFile}' # THIS IS THE VINA DOCK COMMAND

    if vinaPath.exists():
        print('vina exists')
    else:
        print('vina doesnt exist')

    if ligConfig.exists():
        print('ligConfig exists')
    else:
        print('ligconfig doesnt exist')
    print(cmd)

    if logFile.exists():
        print('LogFile exists')
    else:
        print('LogFile doesnt exist...creating one')
        logFile.touch()
    print(cmd)


    # should create ligand_out.pdbqt file which contains the docked ligand
    os.system(cmd)
    cmd = f'move {basePath}\\utilities\\docking\\undocked_ligands\\{filehandle}_out.pdbqt {basePath}\\utilities\\docking\\docked_ligands'

    os.system(cmd)
    # Update progress
    update_progress(task_id=task_id, processed_count=idx)


    return 1



def smi2pdb(col, basePath):

    
    ID = col[0]
    SMI = col[1]

    pdbFile = f'{ID}.pdb'
    
    try:
        # smi = col['Smiles']
        mol = pybel.readstring("smi", SMI)
      
        # strip salt
        mol.OBMol.StripSalts(10)
        mols = mol.OBMol.Separate()
    
        mol = pybel.Molecule(mols[0])
        for imol in mols:
            imol = pybel.Molecule(imol)
            if len(imol.atoms) > len(mol.atoms):
                mol = imol


        mol.addh()
 
        mol.make3D(forcefield='mmff94', steps=100)
        mol.localopt()
       
        os.chdir(f'{basePath}\\utilities\\docking\\undocked_ligands')
        mol.write(format='pdb', filename=str(pdbFile), overwrite=True)
        os.chdir('..\\..\\..\\')
    
        return(1)

    except:
        print(f"transformation {SMI} failed")

    return 0



def parseSmiList(basePath, task_id):



 
    filepath = f'{basePath}\\utilities\\docking\\dataset\\test2.csv'
    

    smiDf = pd.read_csv(filepath)

    
    # Example
    receptor_dir = os.path.join(basePath, 'utilities', 'docking', 'cleaned_receptors')
    all_files = glob.glob(os.path.join(receptor_dir, "*"))

    # Extracting filenames without extensions
    file_names = [os.path.splitext(os.path.basename(file))[0] for file in all_files]



    receptorFile = file_names[0]
    configFile = file_names[0]

   

    configPath = Path(f'{basePath}\\utilities\\docking\\config_files\\{configFile}_config') 

        #if os.path.exists(configPath):
        #    os.system(f'del {configPath}')

    try:
        os.mkdir(configPath) # debug here

    except:
        print('config file directory already exists')

    for idx, col in smiDf.iterrows():
        print(idx, col)
        smi2pdb(col, basePath)
        filehandle = col['ChEMBL ID']
        prepLigand(filehandle, basePath)
        dockSingLig(filehandle, receptorFile, configFile, basePath, idx, task_id=task_id)

    resultsPath = Path(f'{basePath}\\utilities\\docking\\config_files\\{receptorFile}_results')

    #if os.path.exists(resultsPath):
    #    os.system(f'del {resultsPath}')
    
    #os.mkdir(resultsPath)

    src_dir = Path(f'{basePath}\\utilities\\docking\\docked_ligands')
    
    #files = os.listdir(src_dir)

    shutil.copytree(src_dir, resultsPath)






def main():

    

    parser = argparse.ArgumentParser(description='run docking')
    parser.add_argument('--base_directory', type=str, help='Input base directory name', required=True)
    parser.add_argument('--task_id', type=str, help='Unique task ID for progress tracking', required=True)


    #receptorFiles = ['5hk1_cleaned_nolig']
    #configFiles = ['5hk1']

    #base_directory = 'C:\\Users\\patri\\Dropbox\\Ph.D\\OrganoNet\\Websites\\NeuralBind_FEBE\\NeuralBind_BE'
    #parseSmiList(basePath=base_directory)
    args = parser.parse_args()
    parseSmiList(basePath=args.base_directory, task_id=args.task_id) # calls prepLigand: smi -> .pdbqt


    


if __name__ == "__main__":



    main()