#! python3
#renameDeepLearnV1.5.py - looks for loopy-output files in a specified folder
# renames files by replacing the continous number with a well number
# sorts renamed files into a new folder named after the experiment. The folder
# contains sub-folders for day (video number 22-29) and subday (video number 46-
# 52)within this folder, files are sorted into wild-type ("wt", wells A1-C2) and
# mutant("mut", wells C3-E5)

#WARNING: This script works under the assumption that all wells from a plate
# were analysed in consecutive order!!

#Note: Script should work independently of the number of files in the folder
# given that there are exactly 25 files per video. Theoretically, other files in
# the folder should not influence operation.

import shutil
import os
import re
import natsort


#specify working environment (= path where tracking data is saved.)
print('Where are your tracking files?')
trackDirectory = input()
trackDirectory = trackDirectory.replace('\\', '\\')

#specify date of experiment (is added to start of new file name)
print('When where these videos made? Please enter date (YYYYMMDD)')
date = input()

#specify experiment name (is added to end of new file name)
print('What is the name of the experiment?')
experiment = input()

#creating a regular expression to match the Deep Learning output files
DeepLearnFile = re.compile(r""" ^(d\w{29})  #all text before continous number
                           (\d{5})          #continous number
                           (\w+\D)          #text before video number
                           (0\d{5})          #video number
                           (\w+)            #everything after video number
                           """,re.VERBOSE)
#define well names
wells = ['A1','A2','A3','A4','A5','B1','B2','B3','B4','B5',
          'C1','C2','C3','C4','C5','D1','D2','D3','D4','D5',
          'E1','E2','E3','E4','E5']

i = 0  #index used for correct well assignment

#create output folders
mutDay = os.path.join(trackDirectory + '\\' + experiment + '\\day\\mut')
mutSubday = os.path.join(trackDirectory + '\\' + experiment + '\\subday\\mut')
wtDay = os.path.join(trackDirectory + '\\' + experiment + '\\day\\wt')
wtSubday = os.path.join(trackDirectory + '\\' + experiment + '\\subday\\wt')

os.makedirs(mutDay, exist_ok = True)
os.makedirs(mutSubday, exist_ok = True)
os.makedirs(wtDay, exist_ok = True)
os.makedirs(wtSubday, exist_ok = True)

#get list of files matching the regular expression
FileList = os.listdir(trackDirectory)
FileList = natsort.natsorted(FileList)

#loop over all corresponding files in working directory
#creating a new filename, replacing the continous number with well number
#copying file with new name to 'renamed' folder within the same directory

for DeepLearnName in FileList:
    mo = DeepLearnFile.search(DeepLearnName)
    #skip non-matching files
    if mo is None:
        continue
    #identify different parts
    preNum = mo.group(1)
    conNum = mo.group(2)
    tweenText = mo.group(3)
    vidNum = mo.group(4)
    rest = mo.group(5)

    #change conNum to well number (ranging from A1-5 to E1-5)
    wellNum = wells[i]

    #define new filename (date_well_video_experiment)
    analysisName = date + '_' + vidNum + '_' + wellNum + '_' + experiment + '.csv'
    #Get new file path
    if i <= 11 and int(vidNum) < 30:
        analysisName = os.path.join(wtDay, analysisName)
    elif i <= 11 and int(vidNum) > 30:
        analysisName = os.path.join(wtSubday, analysisName)
    elif i > 11 and int(vidNum) < 30:
        analysisName = os.path.join(mutDay, analysisName)
    else:
        analysisName = os.path.join(mutSubday, analysisName)

    DeepLearnName = os.path.join(trackDirectory, DeepLearnName)

    #iterate through 25 wells before starting the numbering again.
    if i < 24:
        i += 1
    else:
        i = 0

    #rename the file
    print('Renaming "%s" to "%s" ...' % (DeepLearnName, analysisName))
    shutil.copy(DeepLearnName, analysisName)

#Version History:
# renameDeepLearnV1.0.py - intial renaming script, renames files, sorts them
#                          into folders corresponding to video number.
# renameDeepLearnV1.1.py - changed sorting to day/subday and wt/mut based on
#                          file name
# renameDeepLearnV1.2.py - fixed sorting with correct well numbers
# renameDeepLearnV1.3.py - fixed bug, where script would stop if output folders
#                          already exist
#                        - fixed bug with incorrect renaming if first digit
#                          of conNum changes
#                        - improved readability
#renameDeepLearnV1.4.py  - fixed issues with varying video nomenclature
#renamDeepLearnV1.5.py   - modified regex pattern to improve identification of video number
        