import os
import sys
try:
    from openbabel import openbabel as ob
except ImportError:
    import openbabel as ob

def filenamePath(inputPath):
    name = os.path.basename(inputPath)
    name = name.replace('_','.').split('.')
    fileName = name[0]
    return fileName




def parseReceptor(receptorFile):
    receptorName = filenamePath(receptorFile)
    print(receptorFile)
    conv = ob.OBConversion()
    conv.SetInFormat("pdbqt")
    receptor = ob.OBMol()
    conv.ReadFile(receptor, receptorFile)

    dockingResults = {
        'name': receptorName,
        'receptor': receptor
    }

    return dockingResults





def parseLigConfig(ligConfigFile):


    ligandName = filenamePath(ligConfigFile)
    # read the scorelist in the pdbqt file
    scorelist = []
    try:
        ligandOutLines = open(ligConfigFile, 'r')
    except FileNotFoundError:
        print("Ligand output file: '%s' can not be found" % (out))
        sys.exit(1)
    for line in ligandOutLines:
        line = line.split()
        if len(line) > 2:
            if line[2] == "RESULT:":
                scorelist.append(line[3])
    # process docking pose of ligands after docking
    convert = ob.OBConversion()
    convert.SetInFormat("pdbqt")
    ligands = ob.OBMol()
    dockedLigands = []
    not_at_end = convert.ReadFile(ligands, ligConfigFile)
    while not_at_end:
        dockedLigands.append(ligands)
        ligands = ob.OBMol()
        not_at_end = convert.Read(ligands)

    docking_results = {
        'docked_ligands': dockedLigands,
        'scorelist': scorelist
    }
    return docking_results







def parseVinaConfig(config_file):

    try:
        configread = open(config_file, 'r')
    except FileNotFoundError:
        print("The config file: '%s' can not be found" % (config_file))
        sys.exit(1)

    configlines = [line for line in configread]
    configread.close()
    # the setting format in the config as : protein_file   name.pdbqt
    for line in configlines:
        uncommented = line.split('#')[0]
        line_list = uncommented.split()

        if not line_list:
            continue
        option = line_list[0]

        if option == "receptorFile":
            receptor = line_list[1]
        elif option == "ligandFolder":
            ligandFolder = line_list[1]
        elif option == "referLigandsFolder":
            referLigandsFolder = line_list[1]
        elif option == "refer_cutoff":
            referCutoff = line_list[1]
        elif option == "hbond_cutoff":
            hbond_cutoff = line_list[1]
        elif option == "halogenbond_cutoff":
            halogenbond_cutoff = line_list[1]
        elif option == "electrostatic_cutoff":
            electrostatic_cutoff = line_list[1]
        elif option == "hydrophobic_cutoff":
            hydrophobic_cutoff = line_list[1]
        elif option == "pistack_cutoff":
            pistack_cutoff = line_list[1]
        elif option == "prepare_ligand4":
            prepareLigand4 = line_list[1]
        elif option == "vinaPath":
            vinaPath = line_list[1]


    parsedResults = {
        'receptor': receptor,
        'ligandFolder': ligandFolder,
        'referLigandsFolder': referLigandsFolder,
        'refer_cutoff': referCutoff,
        'hbond_cutoff': hbond_cutoff,
        'halogenbond_cutoff': halogenbond_cutoff,
        'electrostatic_cutoff': electrostatic_cutoff,
        'hydrophobic_cutoff': hydrophobic_cutoff,
        'pistack_cutoff': pistack_cutoff,
        'prepareLigand4': prepareLigand4,
        'vinaPath': vinaPath
    } 



    return parsedResults