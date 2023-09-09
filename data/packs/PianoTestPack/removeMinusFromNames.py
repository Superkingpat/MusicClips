from os import listdir, rename
from os.path import isfile, join, abspath, dirname

mypath = abspath(dirname(__file__))

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print(mypath)
print(onlyfiles)
for file in onlyfiles:
    rename(mypath+'/'+file,mypath+'/'+file.replace('-',''))