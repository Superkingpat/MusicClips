import moviepy.editor as mp
from os.path import join
import gc


def renderClip(x):
        track = []
        print(x["time"], " - ",(x["time"]+x["duration"]))

        e_time = (x["time"]+x["duration"])

        for y in x["notes"]:
            track.append(mp.VideoFileClip(join(x["pack_name"],(y+".mp4"))).subclip(x["time"],e_time))

        video = mp.CompositeVideoClip(track,size=(1920, 1080))
        video.write_videofile("./Data/helpClips/X"+str(x["index"])+".mp4")
        gc.collect()