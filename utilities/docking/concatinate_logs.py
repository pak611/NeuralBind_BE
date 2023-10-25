
from pathlib import Path
import os




def walk_folder(path, keyword):

    files = os.listdir(path)
    print(f"{len(files)} files have been detected!")
    logFileList = []
    for file in files:
        # print(file)
        if keyword in file:
            logFileList.append(file)

    return logFileList




def combine_logs(configFile):


    #LogFilePath = Path(f'{os.getcwd()}\\config_files\\{fileHandle}')
    logPath = Path(f'{os.getcwd()}\\nbBackend\\docking\\config_files\\{configFile}_config')

    for fileHandle in walk_folder(logPath, 'Compound'):

        combFilePath = Path(f'{os.getcwd()}\\nbBackend\\docking\\config_files\\{configFile}_config\\{configFile}_summaryLog.txt')

        logFilePath = Path(f'{os.getcwd()}\\nbBackend\\docking\\config_files\\{configFile}_config\\{fileHandle}')

        with open(logFilePath, 'r') as logFile:

            lineNumbers = list(range(26,38))

            logSnip = []

            for i, line in enumerate(logFile.readlines()):

                if i in lineNumbers:
                    logSnip.append(line)

        with open(combFilePath, 'a') as combLogFile:
            #combLogFile.seek(0, os.SEEK_END)

            

            combLogFile.write("%s %s %s\n" % (configFile,',',fileHandle.replace('_log.txt','')))
                    
            for line in logSnip:
                combLogFile.write("%s\n" % line)



def combineSummary(summaryPaths):

    baseDir = Path(f'{os.getcwd()}\\nbBackend\\docking\\config_files')

    combinedSummaryPath = Path(f'{os.getcwd()}\\nbBackend\\docking\\finalSummaryLog.txt')


    for summaryPath in summaryPaths:


        summaryFilePath = Path(f'{baseDir}\\{summaryPath}_config\\{summaryPath}_summaryLog.txt')


        num_compounds = 19
        
        with open(summaryFilePath, 'r') as summaryFile:
            lineNumbers = list(range(0, 26 * num_compounds))
            logSnip = []

            for i, line in enumerate(summaryFile.readlines()):

                if i in lineNumbers:
                    logSnip.append(line)
        
        os.remove(summaryFilePath)

        with open(combinedSummaryPath, 'a') as combSum:

            for line in logSnip:
                combSum.write("%s" % line)
        
    

def main():

    configFiles = ['5hk1', '4djh', '5c1m']

    for configFile in configFiles:
        
        combine_logs(configFile)

    
    summaryPaths = ['5hk1', '4djh', '5c1m']

    combineSummary(summaryPaths=summaryPaths)

    print('done')

if __name__ == "__main__":

    main()