from pathlib import Path
import os
import argparse



def runPrepReceptor(filePath, basePath):

    #prepare_receptor = f'{os.getcwd()}\\Tools\\MGLTools-1.5.7\\python_mgl.exe MGLTools-1.5.7_old\\Lib\\site-packages\\prepare_receptor.py'

    prepare_receptor = f'{basePath}\\utilities\\docking\\Tools\\MGLTools-1.5.7\\python_mgl.exe {basePath}\\utilities\\docking\\Tools\\MGLTools-1.5.7\\Lib\\site-packages\\AutoDockTools\\Utilities24\\prepare_receptor4.py'

    #prepare_receptor = f'{os.getcwd()}\\Tools\\MGLTools-1.5.7\\python_mgl.exe {os.getcwd()}\\Tools\\MGLTools-1.5.7\\Lib\\site-packages\\AutoDockTools\\Utilities24\\prepare_receptor4.py'

    file = filePath
    #file = f'{os.getcwd()}\\receptors\\4djh_cleaned_nolig.pdbqt'

    file = Path(file)
    print(f'FILEPATH IS {file}')
    op_file = f'{file.stem}.pdbqt'
    cmd = f"{prepare_receptor} -r {file} -v -o {op_file}"

    os.system(cmd)

    print('finished clean')



    # ... [rest of your function]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepares the receptor.")
    parser.add_argument("--filePath", help="Name of the file to be processed")
    parser.add_argument("--basePath", help='settings.py file base directory for backend')

    args = parser.parse_args()
    runPrepReceptor(args.filePath, args.basePath)