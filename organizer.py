import os
import shutil
from datetime import datetime


def createDir(path:str):
    path = "./"+path
    if not os.path.exists(path):
        os.makedirs(path)

def removeDir(path:str):
    shutil.rmtree(path)

def createMainLayout(main_folder: str):
    path = "./data/history/" + main_folder
    if not os.path.exists(path):
        createDir(path+"/helpClips")
        createDir(path+"/scripts")
    else:
        print("This project already exists!")
        ans = input("Do you want to overwrite it? [Y/N] ").strip().lower()
        if ans == "y" or ans == "j":
            removeDir(path)
            createMainLayout(main_folder)
        elif ans == "n":
            dateTime = datetime.now().strftime("%Y%m%d_%H%M%S")
            createMainLayout(main_folder+"_"+dateTime)

