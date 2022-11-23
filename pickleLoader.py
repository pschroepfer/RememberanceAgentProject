import os
import pickle
import numpy as np


def main():
    fileDict = {}
    filelist = os.listdir('txtList')
    for file in filelist:
        if file == '.DS_Store':
            pass
        else:
            fileLoc = os.path.join('txtList/' + file)
            txtLines = []
            with open(fileLoc, encoding='utf8') as f:
                data = f.read().replace('\n', ' ')
                txtLines.append(data)
            fileDict.update({file: txtLines})
    pickle.dump(fileDict, open('test.pkl', 'wb'))
    return

if __name__ == "__main__":
    main()