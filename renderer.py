import moviepy.editor as mp
from os.path import join
import multiprocessing
import gc
from settings import *

def renderBlockClips(batch_size, blocks):
    pool = multiprocessing.Pool(processes=batch_size)
    pool.map(renderClip, blocks)

def renderClip(x):
    track = []
    for y in x["notes"]:
        clip = mp.VideoFileClip(join(x["pack_name"],(y+".mp4")))
        track.append(clip.subclip(0,clip.duration).set_opacity((1/len(x["notes"]))*(len(x["notes"])-x["notes"].index(y))))

    video = mp.CompositeVideoClip(track,size=(1920, 1080))
    video.write_videofile(HELP_CLIPS_PATH+"/X"+str(x["index"])+".mp4")
    gc.collect()

def renderScriptClips(batch_size, script_list):
    pool = multiprocessing.Pool(processes=round(batch_size/4) )
    pool.map(renderScriptClip, script_list)

def renderScriptClip(script):
    track = []
    start_time = script[0]["time"]

    for y in script:
        if (y["note"][0] != 'X'):
            clip = mp.VideoFileClip(join(PACK_NAME,(y["note"]+".mp4")))
        else:
            clip = mp.VideoFileClip(join(HELP_CLIPS_PATH,(y["note"]+".mp4")))
        track.append(clip.set_start(y["time"]-start_time))

    video = mp.CompositeVideoClip(track,size=(1920, 1080))
    video.write_videofile(HELP_CLIPS_PATH+"/Y"+str(y["index"])+".mp4")
    gc.collect()

def renderFinal(script):
    track = []
    for line in script:
        clip = mp.VideoFileClip(join(HELP_CLIPS_PATH,(line["note"]+".mp4")))
        track.append(clip.set_start(line["time"]))

    video = mp.CompositeVideoClip(track,size=FULL_HD)
    video.write_videofile("movie.mp4")
    