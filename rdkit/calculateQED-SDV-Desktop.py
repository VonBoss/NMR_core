#!/usr/bin/env python3
# -----------------------------------------------------
# Calculate QED scores
# Seth Veenbaas
# Weeks Lab, UNC-CH
# 2024
#
# Version 1.1.0
#
# -----------------------------------------------------

import pandas as pd
from glob import glob
from rdkit import Chem
from rdkit.Chem import AllChem, QED, PandasTools, rdMolDescriptors, Crippen
import argparse
from pathlib import Path

### PandasTools settings
PandasTools.InstallPandasTools()
PandasTools.RenderImagesInAllDataFrames(images=True)

def make_from_smiles(
    csv : str | Path,
    out : str | Path,
    properties : bool,
    moldescriptor : bool,
    geometry : bool,
):
        
    smiles_df = pd.read_csv(csv)
    smiles_col = [col for col in smiles_df.columns if 'SMILES' in col][0]
    smiles_df[smiles_col] = smiles_df[smiles_col].astype(str)

    PandasTools.AddMoleculeColumnToFrame(smiles_df, smilesCol=smiles_col, molCol='ROMol', includeFingerprints=True)
    smiles_df = smiles_df[smiles_df['ROMol'].apply(lambda x: x.HasSubstructMatch(Chem.MolFromSmiles('C')))]    

    smiles_df['3DMol'] = smiles_df['ROMol'].apply(generate_conformer_and_optimize)

    add_qed(smiles_df, out, csv, properties, moldescriptor, geometry)
    

def make_from_sdf(
    sdf : str | Path,
    out : str | Path,
    properties : bool,
    moldescriptor : bool,
    geometry : bool,
):

    name = Path(sdf).stem 
    string_sdf = str(sdf)
    
    sdf_df = PandasTools.LoadSDF(string_sdf, idName='ID', molColName='ROMol', includeFingerprints=False, isomericSmiles=True, smilesName='SMILES', embedProps=True, removeHs=False, strictParsing=True)
    
    sdf_df['3DMol'] = sdf_df['ROMol'].apply(generate_conformer_and_optimize)
    
    add_qed(sdf_df, out, sdf, properties, moldescriptor, geometry)


def generate_conformer_and_optimize(mol : Chem.rdchem.Mol):
    mol = Chem.AddHs(mol)  # Add hydrogens
    status = AllChem.EmbedMolecule(mol)  # Generate a conformer
    if status != 0:  # Embedding failed
        print(f"Failed to embed molecule: {Chem.MolToSmiles(mol)}")
        return None
    AllChem.UFFOptimizeMolecule(mol)  # Optimize the conformer geometry
    return mol


def add_qed(
    df : pd.DataFrame,
    out : str | Path,
    file : str | Path,
    properties : bool,
    moldescriptor : bool,
    geometry : bool,
):

    df['QED'] = df['ROMol'].apply(lambda x: QED.default(x))
    if properties:
            df = get_qed_properties(df, molcol='ROMol')
    if moldescriptor:
            df = get_mol_decriptors(df, molcol='ROMol')
    if geometry:
            df = get_geometry(df, molcol='3DMol')


    save_df(df=df, out=out, file=file, molcol=['ROMol', '3DMol'])


def save_df(
    df : pd.DataFrame,
    out : str | Path,
    file : str | Path,
    molcol : str | list,
):
    if out:
        dir = Path(out)
    else:    
        dir = Path(file).parent
    if not dir.is_dir():
        dir.mkdir()
    file_name = Path(file).stem
    sdf_out = str(Path(dir, file_name + "_qed.sdf"))
    
    print(f'Saving {sdf_out} ....')
    PandasTools.WriteSDF(df, sdf_out, molColName=molcol[-1], properties=list(df.columns))

    print(f'Saving {Path(dir, file_name + "_qed.xlsx")} ....')
    PandasTools.SaveXlsxFromFrame(df, Path(dir, file_name + '_qed.xlsx'), molCol=molcol, size=(150, 150))

    try:         
        df.to_html(Path(dir, file_name + "_qed.html"))
        print(f'Saving {Path(dir, file_name + "_qed.html")} ....')  
    except:
        print("Unable to save .HTML file.")

    
    print('Done!')


def get_qed_properties(df : pd.DataFrame, molcol : str):
    try:
        df['MW'] = df[molcol].apply(lambda x: QED.properties(x)[0])
        df['ALOGP'] = df[molcol].apply(lambda x: QED.properties(x)[1])
        df['HBA'] = df[molcol].apply(lambda x: QED.properties(x)[2])
        df['HBD'] = df[molcol].apply(lambda x: QED.properties(x)[3])
        df['PSA'] = df[molcol].apply(lambda x: QED.properties(x)[4])
        df['ROTB'] = df[molcol].apply(lambda x: QED.properties(x)[5])
        df['AROM'] = df[molcol].apply(lambda x: QED.properties(x)[6])
        df['ALERTS'] = df[molcol].apply(lambda x: QED.properties(x)[7])
    except:
        pass

    return df

def get_mol_decriptors(df : pd.DataFrame, molcol : str):

    try:
        df['Num Ring'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNumRings(x))
        df['Num Ar Ring'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNumAromaticRings(x))
        df['Num ArHetcy'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNumAromaticHeterocycles(x))
        df['Num Hetcy'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNumHeterocycles(x))
        df['Num Hetatm'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNumHeteroatoms(x))
        df['Num Spiro'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNumSpiroAtoms(x))
        df['Frac Sp3'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcFractionCSP3(x))
        df['MR'] = df[molcol].apply(lambda x: Crippen.MolMR(x))
    except:
        pass

    return df


def get_geometry(df : pd.DataFrame, molcol : str):
    try:
        # Calculate normalized principle ratios
        df['NPR1'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNPR1(x))
        df['NPR2'] = df[molcol].apply(lambda x: rdMolDescriptors.CalcNPR2(x))
        
        # Get ligand geometry
        df['Geometry'] = 'Balanced'
        df.loc[df.eval('NPR1 - NPR2 + 0.5 < 0'), 'Geometry'] = 'Rod-like'
        df.loc[df.eval('- NPR1 - NPR2 + 1.5 < 0'), 'Geometry'] = 'Sphere-like'
        df.loc[df.eval('NPR2 - 0.75 < 0'), 'Geometry'] = 'Disc-like'
    except:
        pass

    return df

def parseArgs():
    prs = argparse.ArgumentParser()
    ex_group = prs.add_mutually_exclusive_group()

    ex_group.add_argument('-d', '--dir', type=Path,
                     help='Path to a directory containing input .sdf files.')
    
    ex_group.add_argument('-csv', '--csv', type=Path,
                    help='Specify a *smiles*.csv files. '
                    'File name much contain "smiles" and the SMILES string much '
                    'be in a column titled "SMILES".')
    
    ex_group.add_argument('-sdf', '--sdf', type=Path,
                    help='Path to an input .sdf file.')
    
    prs.add_argument('-o', '--out', type=Path, default = None,
                     help='Path to output directory. (Default=directory of input file)')
    
    prs.add_argument('-p', '--properties', action='store_true', default = False,
                     help='Adds QED properties to outputs. (Default=False)')
    
    prs.add_argument('-md', '--moldescriptors', action='store_true', default = False,
                     help='Adds QED properties to outputs. (Default=False)')

    prs.add_argument('-g', '--geometry', action='store_true', default = False,
                     help='Adds NPR1, NPR2, and geometry descriptor to outputs. (Default=False)')

    args = prs.parse_args()
    return args


def main(
    dir : str | Path,
    csv : str | Path,
    sdf : str | Path,
    out : str | Path,
    properties : bool,
    moldescriptors : bool,
    geometry : bool,
):
    print('Calculating properties...')
    if csv:
        make_from_smiles(csv, out, properties, moldescriptors, geometry)
    elif sdf:
        make_from_sdf(sdf, out, properties, moldescriptors, geometry)
    elif dir:
        sdf_files = glob(f"{dir}/*.sdf")
        for sdf in sdf_files:
            make_from_sdf(sdf, out, properties, moldescriptors, geometry)

if __name__ == "__main__":
    main(**vars(parseArgs()))
