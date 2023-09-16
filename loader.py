import moviepy.editor as mp
from os import listdir
from os.path import isfile, join
from settings import *

def loadBaseClips(pack_name, note_list):
    only_files = [f.replace(".mp4","") for f in listdir(pack_name) if (isfile(join(pack_name, f)) and f.endswith(".mp4"))]
    clip_array = {}
    for f in only_files:
        if f in note_list:
            clip_array[f] = mp.VideoFileClip(join(pack_name,(f+".mp4")))

    return clip_array

def loadHelpClips(clip_array = {}):
    only_files = [f.replace(".mp4","") for f in listdir(HELP_CLIPS_PATH) if (isfile(join(HELP_CLIPS_PATH, f)) and f.endswith(".mp4"))]
    for f in only_files:
        clip_array[f] = mp.VideoFileClip(join(HELP_CLIPS_PATH,(f+".mp4")))
    return clip_array

def loadAllClips(pack_name, clip_array = {}):
    only_files = [f.replace(".mp4","") for f in listdir(pack_name) if (isfile(join(pack_name, f)) and f.endswith(".mp4"))]
    for f in only_files:
        clip_array[f] = mp.VideoFileClip(join(pack_name,(f+".mp4")))
    return clip_array
