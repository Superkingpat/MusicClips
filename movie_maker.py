import moviepy.editor as mp
import json
import multiprocessing
from os import listdir
from os.path import isfile, join
#from ClipRenderer import renderClip
import gc

NOTELIST = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#" ,"G", "G#"]
FULL_HD = (1920, 1080)
BATCH_SIZE = 10  #No more than 10 batches
AUDIO_OFFSET = 0.5 #Seconds of offset
KEEP_LOGS = True 
HELP_CLIPS = "./data/helpClips"
PACK_NAME = "./data/packs/PianoTestPack"

def main(presses: list[dict]):
    gc.enable()

    script = json.load(open(r'./data/music.json'))
    
    pack_name = './data/packs/' +  "PianoTestPack"#input('Ime paketa: ')

    script = checkScript(script, pack_name)

    note_list, script, blocks = optimizeScript(script, pack_name)

    script_list, final_script = splitLoad(script)

    renderBlockClips(BATCH_SIZE, blocks)

    renderScriptClips(BATCH_SIZE, script_list)

    renderFinal(final_script)

def vertical(composite: mp.CompositeVideoClip, video_clips: list[mp.VideoClip]) -> mp.VideoClip:
    pass

def horizontal(composite: mp.CompositeVideoClip, video_clips: list[mp.VideoClip]) -> mp.VideoClip:
    pass

## HELP FUNCTIONS ##

def sort(set):
    set = list(set)
    for x in range(0,len(set)):
        for y in range(x+1,len(set)):
            if (midiValue(set[x]) > midiValue(set[y])):
                set[x], set[y] = set[y], set[x]
    return set
    
def midiValue(keyCode):
    return int(keyCode[-1])*12+int(NOTELIST.index(keyCode.rstrip(keyCode[-1])))

def keyCode(midiValue):
    return NOTELIST[midiValue%12] + str(int(midiValue/12)) 

####################

# MODIFY & VALIDATE #

def checkScript(script, pack_name):
    script_notes = set()
    pack_notes = sort([f.replace(".mp4","") for f in listdir(pack_name) if (isfile(join(pack_name, f)) and f.endswith(".mp4"))])
    missing_notes = []

    for x in script:
        script_notes.add(x["note"])

    for note in script_notes:
        if (note not in pack_notes):
            missing_notes.append(note)

    script_notes = sort(script_notes)

    if missing_notes != []:
        print("Song range: ", script_notes[0], " - ", script_notes[-1])
        print("Pack range: ", pack_notes[0], " - ", pack_notes[-1])
        print("Missing notes: ", missing_notes)

        if (midiValue(script_notes[-1]) - midiValue(script_notes[0]) < midiValue(pack_notes[-1]) - midiValue(pack_notes[0])):
            print("It's possible to transpose the song.")

            print("Where to you want to transpose song? MIN:",  (midiValue(pack_notes[0]) - midiValue(script_notes[0])), " MAX:", (midiValue(pack_notes[-1]) - midiValue(script_notes[-1])))
            value = int(input())
            if (midiValue(pack_notes[0]) - midiValue(script_notes[0])) < value and (midiValue(pack_notes[-1]) - midiValue(script_notes[-1]) > value and value != 0):
                return transpose(value, script, pack_name)
            
    return script

def transpose(num: int, script, pack_name):
    for x in range(0,len(script)):
        script[x]["note"] = keyCode(midiValue(script[x]["note"]) + num)
    return script

def instrumentToPack(script):
    pass

def optimizeScript(script, pack_name):
    note_list = set() #USED NOTES
    new_script = []
    tmp_script = {"time": 0, "duration": 0}
    blocks = []
    notes = []
    shorten = False
    index = 0
    note_array = []

    for i in range(0,len(script)):
        if (len(script) == i):
            note_list.add(script[i-1]["note"])
            new_script.append(script[i-1])
            if (shorten):
                new_script[-1]["note"] = "X" + str(index)
                blocks.append({"notes": notes, "time": script[i]["time"], "duration": script[i]["duration"], "index": index, "pack_name": pack_name})
                index += 1
                tmp_script = {"time": 0, "duration": 0}
                notes = []
                shorten = False
            break

        if (tmp_script["time"] == script[i]["time"] and tmp_script["duration"] == script[i]["duration"]): #If note has same time and duration as previous one
            if (not shorten):
                notes.append(script[i-1]["note"])
            notes.append(script[i]["note"])
            shorten = True
            continue
        elif (tmp_script["time"] != 0 and tmp_script["duration"] != 0): #add note to script
            note_list.add(script[i-1]["note"])
            new_script.append(script[i-1])

            if (shorten): # write a block
                sort(notes)
                if notes in note_array:
                    new_script[-1]["note"] = "X" + str(note_array.index(notes))
                else:
                    new_script[-1]["note"] = "X" + str(index)
                    note_array.append(notes)
                    blocks.append({"notes": notes, "index": index, "pack_name": pack_name})
                    index += 1
                notes = []
                shorten = False
            tmp_script = {"time": 0, "duration": 0}

        if (tmp_script["time"] == 0 and tmp_script["duration"] == 0):
            tmp_script["time"] = script[i]["time"]
            tmp_script["duration"] = script[i]["duration"]

    file = open("optimisedScript.json", "w")
    file.write(json.dumps(new_script).replace("},", "},\n"))

    file = open("blocks.json", "w")
    file.write(json.dumps(blocks).replace("},", "},\n"))

    gc.collect()

    return note_list, new_script, blocks

def splitLoad(script):
    output = []
    tmp = []
    final_script = []
    count = 0
    if (len(script) / 100 > BATCH_SIZE):
        #Deli na datoteke po 100 not
        for x in range(0,len(script)):
            tmp.append(script[x])
            tmp[-1]["index"] = count
            if ((x+1) % 101 == 0):
                output.append(tmp)
                final_script.append({"note": "Y"+str(count), "time": tmp[0]["time"]})
                tmp = []
                count += 1
    elif (len(script) < 100):
        for x in script:
            tmp.append(x)
            tmp[-1]["index"] = 0
    else:
        #Razdeli na enakomerne datoteke do 100 not
        num_of_elements = round(len(script) / BATCH_SIZE)
        print(num_of_elements)
        for x in range(0,len(script)):
            tmp.append(script[x])
            tmp[-1]["index"] = count
            if ((x+1) % num_of_elements == 0):
                output.append(tmp)
                final_script.append({"note": "Y"+str(count), "time": tmp[0]["time"]})
                tmp = []
                count += 1

    if (tmp != []):
        output.append(tmp)
        final_script.append({"note": "Y"+str(count), "time": tmp[0]["time"]})

    file = open("splitedScript.json", "w")
    file.write(json.dumps(output).replace("},", "},\n"))

    file = open("final_script.json", "w")
    file.write(json.dumps(final_script).replace("},", "},\n"))

    gc.collect()

    return output, final_script

#####################

####  RENDERER  ####

def renderBlockClips(batch_size, blocks):
    if __name__ == '__main__':
        pool = multiprocessing.Pool(processes=batch_size)
        pool.map(renderClip, blocks)

def renderClip(x):
    track = []
    for y in x["notes"]:
        clip = mp.VideoFileClip(join(x["pack_name"],(y+".mp4")))
        track.append(clip.subclip(0,clip.duration).set_opacity((1/len(x["notes"]))*(len(x["notes"])-x["notes"].index(y))))

    video = mp.CompositeVideoClip(track,size=(1920, 1080))
    video.write_videofile(HELP_CLIPS+"/X"+str(x["index"])+".mp4")
    gc.collect()

def renderScriptClips(batch_size, script_list):
    if __name__ == '__main__':
        pool = multiprocessing.Pool(processes=round(batch_size/4) )
        pool.map(renderScriptClip, script_list)

def renderScriptClip(script):
    track = []
    start_time = script[0]["time"]

    for y in script:
        if (y["note"][0] != 'X'):
            clip = mp.VideoFileClip(join(PACK_NAME,(y["note"]+".mp4")))
        else:
            clip = mp.VideoFileClip(join(HELP_CLIPS,(y["note"]+".mp4")))
        track.append(clip.set_start(y["time"]-start_time))

    video = mp.CompositeVideoClip(track,size=(1920, 1080))
    video.write_videofile(HELP_CLIPS+"/Y"+str(y["index"])+".mp4")
    gc.collect()

def renderFinal(script):
    track = []
    for line in script:
        clip = mp.VideoFileClip(join(HELP_CLIPS,(line["note"]+".mp4")))
        track.append(clip.set_start(line["time"]))

    video = mp.CompositeVideoClip(track,size=FULL_HD)
    video.write_videofile("movie.mp4")

####################

####   LOADER   ####

def loadBaseClips(pack_name, note_list):
    only_files = [f.replace(".mp4","") for f in listdir(pack_name) if (isfile(join(pack_name, f)) and f.endswith(".mp4"))]
    clip_array = {}
    for f in only_files:
        if f in note_list:
            clip_array[f] = mp.VideoFileClip(join(pack_name,(f+".mp4")))

    return clip_array

def loadHelpClips(clip_array = {}):
    only_files = [f.replace(".mp4","") for f in listdir(HELP_CLIPS) if (isfile(join(HELP_CLIPS, f)) and f.endswith(".mp4"))]
    for f in only_files:
        clip_array[f] = mp.VideoFileClip(join(HELP_CLIPS,(f+".mp4")))
    return clip_array

def loadAllClips(pack_name, clip_array = {}):
    only_files = [f.replace(".mp4","") for f in listdir(pack_name) if (isfile(join(pack_name, f)) and f.endswith(".mp4"))]
    for f in only_files:
        clip_array[f] = mp.VideoFileClip(join(pack_name,(f+".mp4")))
    return clip_array

####################

SPLIT_TEMPLATE_NAMES = {
    'vertical': vertical,
    'horizontal': horizontal,
}

if __name__ == '__main__':
    main([])