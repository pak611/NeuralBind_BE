


import pandas as pd

df = pd.DataFrame({'Molecule': [1,2,3], 'SMILES': [4,5,6]})

print(f'dataframe is {df}')


df2 = pd.DataFrame({'Molecule':[], 'SMILES':[]})
df2['smi'] = df2.apply(
    lambda x: df.loc[x['Molecule'], 'SMILES'], axis=1)


print('what happened')