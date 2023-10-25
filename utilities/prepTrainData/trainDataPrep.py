from model.toolkits.parse_tool import parseLigConfig,parseReceptor,parseVinaConfig
import os
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import rdkit
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem, QED
try:
    from openbabel import pybel
except:
    import pybel
# from metrics_utils import logP, QED, SA, weight, NP
from functools import partial
from multiprocessing import Pool
from tqdm.auto import tqdm
from pandarallel import pandarallel
#from pandarallel.core import pandarallel




def getParser():
    
    print('what is wrong with the syntax?')

    defaultDataset = f'{os.getcwd()}\\utilities\\fingerprint\\IFP_ResIFP.csv'
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--info",
        help=
        "File path of ligands information, including docking score, SMILES etc.",
        default='')
    parser.add_argument("--dataset",
                        help="IFP dataset path",
                        type=str,
                        default= defaultDataset)
    parser.add_argument("--type",
                        help="model type: aifp,ecfp or dScorePP",
                        type=str,
                        default='dScorePP')
    args = parser.parse_args()
    return args


def calEcfp(smi):
    try:
        smi = list(smi)[0]
        print(smi)
        mol = Chem.MolFromSmiles(smi)
        ecfp = AllChem.GetMorganFingerprintAsBitVect(mol, 3, nBits=1024)
        return list(ecfp)
    except Exception as e:
        print(e)
        return []


def calProps(smi):
    try:
        smi = list(smi)[0]
        mol = Chem.MolFromSmiles(smi)
        logp = Descriptors.MolLogP(mol)
        tpsa = Descriptors.TPSA(mol)
        molwt = Descriptors.ExactMolWt(mol)
        hba = rdMolDescriptors.CalcNumHBA(mol)
        hbd = rdMolDescriptors.CalcNumHBD(mol)
        qed = QED.qed(mol)
        return logp, tpsa, molwt, hba, hbd, qed  #['logP', 'TPSA', 'MW', 'HBA', 'HBD', 'QED']
    except Exception as e:
        print(e)
        return []




def prepareEcfp(args):
    dfIFP = pd.read_csv(args.dataset).set_index('Molecule', drop=False)
    dfInfo = pd.read_csv(args.info).set_index('Name', drop=False)

    ##  Get SMILES
    pandarallel.initialize()
    dfIFP['smi'] = dfIFP.parallel_apply(
        lambda x: dfInfo.loc[x['Molecule'], 'SMILES'], axis=1)
    ## Calculate ECFP fingerprint
    new_columns = [f'ecfp{i}' for i in range(1024)]
    df_IFP[new_columns] = df_IFP.parallel_apply(
        lambda x: calEcfp(dfInfo.loc[x['Molecule'], ['SMILES']]),
        axis=1,
        result_type='expand')
    suffix = '_ecfpSmi.csv'
    # df = df.sort_values(by='score_0', ascending=True)
    outdf = args.dataset.replace('.csv', suffix)
    df_IFP = df_IFP.dropna(axis=0, how='any')
    # df['score_0'] = df['score_0'].astype(float)
    # if not os.path.exists(outdf):
    df_IFP.to_csv(outdf, index=False)

def prepareDScorePPropIFP(args):
    dfIFP = pd.read_csv(args.dataset).set_index('Molecule', drop=False)
    print('lets see what it looks like')
    dfInfo = pd.read_csv(args.info).set_index('Name', drop=False)

    ##  Get SMILES
    pandarallel.initialize()
    dfIFP[['smi', 'score_0']] = dfIFP.parallel_apply(
        lambda x: dfInfo.loc[x['Molecule'], ['SMILES', 'Docking_score']],
        axis=1)

    ## Calculate physical properties
    newColumns = ['logP', 'TPSA', 'MW', 'HBA', 'HBD', 'QED']
    dfIFP[newColumns] = df_IFP.parallel_apply(
        lambda x: calProps(dfInfo.loc[x['Molecule'], ['SMILES']]),
        axis=1,
        result_type='expand')
    suffix = '_dScorePP.csv'
    # df = df.sort_values(by='score_0', ascending=True)
    outdf = args.dataset.replace('.csv', suffix)
    df_IFP = df_IFP.dropna(axis=0, how='any')
    # df['score_0'] = df['score_0'].astype(float)
    # if not os.path.exists(outdf):
    df_IFP.to_csv(outdf, index=False)


def prepareIFPsmi(args):
    df_IFP = pd.read_csv(args.dataset).set_index('Molecule', drop=False)
    df_info = pd.read_csv(args.info).set_index('Name', drop=False)

    ##  Get SMILES
    df_IFP['smi'] = df_IFP.apply(
        lambda x: df_info.loc[x['Molecule'], 'SMILES'], axis=1) # defines lambda one-liner input x
    suffix = '_AIFPsmi.csv'
    outdf = args.dataset.replace('.csv', suffix)
    df_IFP = df_IFP.dropna(axis=0, how='any')
    # if not os.path.exists(outdf):
    df_IFP.to_csv(outdf, index=None)
    pass




def main(args):

    if args.type == 'ecfp':
        prepareEcfp(args)
    elif args.type == 'dScorePP':
        prepareDScorePPropIFP(args)
    elif args.type == 'aifp':
        prepareIFPsmi(args)
    
'''

def main(args):
    prepareIFPsmi(args)

'''
if __name__ == "__main__":
    args = getParser()
    main(args)