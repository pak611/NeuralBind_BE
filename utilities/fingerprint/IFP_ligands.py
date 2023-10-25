from __future__ import print_function
import pickle
from model.toolkits.interactions import close_contacts
from model.toolkits.interactions import hydrophobic_contacts
from model.toolkits.interactions import salt_bridges
import numpy as np
import pandas as pd
# from bitarray import bitarray
try:
    # Open Babel >= 3.0
    from openbabel import openbabel as ob
except ImportError:
    import openbabel as ob
import sys
import os
import argparse
# from time import time
from model.toolkits.parse_tool import parseLigConfig, parseReceptor, parseVinaConfig
# from model.toolkits.parse_conf import parse_config
# from model.toolkits.parse_docking_conf import parse_vina_conf
from model.toolkits.PARAMETERS import HYDROPHOBIC, AROMATIC, HBOND, ELECTROSTATIC, HBOND_ANGLE,\
    AROMATIC_ANGLE_LOW, AROMATIC_ANGLE_HIGH
from model.obbl import Molecule
from model.toolkits.spatial import angle, distance
from model.toolkits.interactions import hbonds, pi_stacking, salt_bridges, \
    hydrophobic_contacts, close_contacts, halogenbonds
from model.toolkits.pocket import pocket_atoms
from model.IFP import cal_Interactions,  get_Molecules, cal_IFP
from pathos.multiprocessing import Pool
from functools import partial
from tqdm.auto import tqdm
from pathlib import Path



def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="config",
                        default='C:\\Users\\patri\\Dropbox\\Ph.D\\OrganoNet\\NeuralBind\\utilities\\fingerprint\\config_files\\config_ifp.txt')
    parser.add_argument("--save", help="dataframe name of IFP",
                        default='IFP')
    parser.add_argument("--n_jobs", help="number of threads", type=int,
                        default=10)
    args = parser.parse_args()
    return args


def saveObj(obj, name):
    print(F'WORKING DIRECTORY IS {os.getcwd()}')
    os.system('mkdir obj')
    with open('/utilities/fingerprint/obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    

def loadObj(name):
    print(f'WORKING DIRECTORY IS {os.getcwd()}')
    
    load_path = os.getcwd() + '\\utilities\\fingerprint\\obj\\' + name + '.pkl'
    print(f'opening {load_path}')

    with open(os.getcwd() + '\\utilities\\fingerprint\\obj\\' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

'''
def collectOutFiles(referLigandsFolder):
    suffix = '_out.pdbqt'
    processed = [] # initialize empty files list
    files = os.listdir(referLigandsFolder)
    for file in files:
        baseName = os.path.basename(file)
        simpleName = baseName.replace('_', '.').split('.') # returns a list of filename words split
        simpleName = simpleName[0]
        processed.append({
            'simpleName': simpleName,
            'baseName': baseName,
            'fullName': file
        }) # list of dictionary values?

        return processed

'''

def collectOutFiles(path):
    suffix = '_out.pdbqt'
    processed = []
    files = os.listdir(path)
    print(f"{len(files)} files have been detected!")
    outpdbqt = []
    for file in files:
        # print(file)
        if suffix in file:
            outpdbqt.append(file)
    #         base_name = os.path.basename(file)
    #         # print(base_name)
    #         simple_name = base_name.replace('_', '.').split('.')
    #         simple_name = simple_name[0]
    #         processed.append({'simple_name': simple_name,
    #                           'base_name': base_name, 'full_name': file})
    # # print(processed)
    return outpdbqt

def concatDf(dicMain, dic):
    # df_interaction = ''
    # for i in range(len(df_res)):
    #     if i == 0:
    #         df_interaction = df_res[0]
    #     else:
    #         for key in df_interaction.keys():
    #             df_interaction[key] = pd.concat(
    #                 [df_interaction[key], df_res[i][key]])
    # return df_interaction
    for key in dicMain.keys():
        if len(dicMain[key]) == 0:
            dicMain[key] = dic[key]
        else:
            dicMain[key] = pd.concat([dicMain[key], dic[key]])
    return dicMain

def calInteracionsRun(ligand, mol_p, config):
    ''' This funciton will calculate all the intercations between the protein and all the docking poses of the ligand.
    '''
    ligandName = ligand['simple_name']
    ligandFolder = config['ligandFolder']
    ligand = parseLigConfig(os.path.join(
        ligandFolder, ligand['base_name']))
    ligandPoses = ligand['docked_ligands']
    interactionPoses = []
    for ipose in range(len(ligandPoses)):
        mol_l = Molecule(ligandPoses[ipose], protein=False)
        df_res = cal_Interactions(
            mol_p, mol_l, config)
        print(f"\n{ligandName}-{ipose}\n")
        for key in df_res.keys():
            df_res[key]['Molecule'] = f'{ligandName}-{ipose}'
        interactionPoses.append(df_res)
    return interactionPoses


def IFP(ligand, config):
    '''The  interaction types of different ligand poses will be transformed into interaction fingerprint.
    '''
    receptor = config['receptor']
    receptor = parseReceptor(receptor)
    mol_p = Molecule(receptor['receptor'], protein=True)
    baseName = os.path.basename(ligand)

    # print(base_name)
    simpleName = baseName.replace('_out.pdbqt', '')
    processed = {'simple_name': simpleName,
                 'base_name': baseName, 'full_name': ligand}
    interactionPoses = calInteracionsRun(processed, mol_p, config)
    referenceAtom = loadObj('referAtomsList')
    referenceRes = loadObj('referResList')
    IFPPoses = []
    for ipose in range(len(interactionPoses)):
        if ipose < 5:
            # the IFPs are python list.
            AAIFP, RESIFP = cal_IFP(
                interactionPoses[ipose], referenceAtom, referenceRes)
            AAIFP = [f'{simpleName}_{ipose}']+AAIFP
            RESIFP = [f'{simpleName}_{ipose}']+RESIFP
            IFPPoses.append([AAIFP, RESIFP])
    return IFPPoses



def main(config, args):
    debug = 0  # if in debug model 0: False  1: True
    dfInteraction = {'df_hbond': '', 'df_halogen': '',
                      'df_elecpair': '', 'df_hydrophobic': '', 'df_pistack': ''}
    receptor = config['receptor']
    ligandFolder = config['ligandFolder']
    ligands = collectOutFiles(ligandFolder)
    receptor = parseReceptor(receptor)
    mol_p = Molecule(receptor['receptor'], protein=True)

    with Pool(10) as pool:
        IFPp = partial(
            IFP,  config=config)
        resList = [x for x in tqdm(
            pool.imap(IFPp, list(ligands)),
            total=len(ligands),
            miniters=50
        )
            if x is not None]
    AAIFPFull = []
    ResIFPFull = []
    for IFPPoses in resList:
        for iPose in IFPPoses:
            AAIFPFull.append(iPose[0])
            ResIFPFull.append(iPose[1])

    # df_Interaction = concat_df(df_res)
    reference_atom = loadObj('referAtomsList')
    reference_res = loadObj('referResList')
    colname = ['Molecule']
    for iatm in reference_atom:
        for iifp in ['hbd', 'halg', 'elec', 'hrdr', 'pipi']:
            colname.append(f'{iatm}-{iifp}')

    AAIFPFull = pd.DataFrame(
        AAIFPFull, columns=colname)
    colname = ['Molecule']
    for ires in reference_res:
        for iifp in ['hbd', 'halg', 'elec', 'hrdr', 'pipi']:
            colname.append(f'{ires}-{iifp}')
    ResIFPFull = pd.DataFrame(
        ResIFPFull, columns=colname)
    AAIFPFull.to_csv(f'{os.getcwd()}\\utilities\\fingerprint\\{args.save}_AAIFP.csv', index=None)
    ResIFPFull.to_csv(f'{os.getcwd()}\\utilities\\fingerprint\\{args.save}_ResIFP.csv', index=None)
    print('SAVE TO')


if __name__ == "__main__":
    args = getParser()
    config = parseVinaConfig(args.config)
    main(config, args)

