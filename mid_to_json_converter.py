import os
import json
from math import floor
from settings import MIDIS_PATH, JSONS_PATH, NOTE_LIST

try:
    from mido import MidiFile
except ImportError:
    print("Importing mido")
    os.system('cmd /c "pip install mido"')
    from mido import MidiFile

channel_filter = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ]
minimum_start_delay = 2 # [s]


def convert(filename: str = ""):
        global channel_filter, minimum_start_delay

        in_path = os.path.join(MIDIS_PATH, filename)+".mid"
        out_path = os.path.join(JSONS_PATH, filename)+".json"

        print(in_path)
        print(out_path)

        # Construct note actions out of the midi data
        midi_note_actions = []
        for message in MidiFile(in_path).play():
            message = str(message).split()
            
            state = None
            channel = None
            note = None
            time = None
            for element in message:
                if element == "note_on": state = True
                elif element == "note_off" or state and element[:8] == "velocity" and element.split("=")[1] == "0": state = False
                elif element[:7] == "channel": channel = int(element.split("=")[1])
                elif element[:4] == "note":
                    note_index = int(element.split("=")[1])
                    note = NOTE_LIST[note_index % 12] + str(floor(note_index / 12) - 1)
                elif element[:4] == "time": time = float(element.split("=")[1])
            if channel not in channel_filter or state == None or note == None or time == None: continue
            
            if len(midi_note_actions) > 0: time += midi_note_actions[-1]["time"]
            
            midi_note_actions.append({ "state":state, "note":note, "channel":channel, "time":time })

            print(midi_note_actions[-1])
            
        
        # convert { true, C1, time = 1.5 } and { false, C1, time = 2.5 } to { C1, time = 1.5, duration = 1 }
        print("Converting …")
        note_presses = []
        index = 0
        while True:
            release_index = index + 1
            while midi_note_actions[release_index]["note"] != midi_note_actions[index]["note"] or midi_note_actions[release_index]["channel"] != midi_note_actions[index]["channel"]:
                release_index += 1
            if release_index >= len(midi_note_actions): break

            note = midi_note_actions[index]["note"]
            time = midi_note_actions[index]["time"]
            instrument = channel_filter.index(midi_note_actions[index]["channel"])
            duration = midi_note_actions[release_index]["time"] - midi_note_actions[index]["time"]
            note_presses.append({"note":note, "instrument":instrument, "time":time, "duration":duration })

            print(len(note_presses), note_presses[-1])

            next_index = index + 1
            while midi_note_actions[next_index]["state"] == False and next_index + 1 < len(midi_note_actions):
                next_index += 1
            index = next_index
            if index >= len(midi_note_actions) - 1: break

        # Add start delay if necessary
        if note_presses[0]["time"] < minimum_start_delay:
            time_shift = minimum_start_delay - note_presses[0]["time"]
            print(f"Shifting time for {time_shift}s …")
            for note_press in note_presses:
                note_press["time"] += time_shift
        
        # Sort notes that start at the same time by channel in descending order
        """print("Sortiram …")
        t_end = note_presses[-1]["time"]
        note_presses.sort(key=lambda press: (t_end-press["time"], press["instrument"]), reverse=True)"""

        # Compress channel numbering
        print("compressing channels …")
        non_empty_channels = []
        for note_press in note_presses:
            if note_press["instrument"] not in non_empty_channels:
                non_empty_channels.append(note_press["instrument"])
        non_empty_channels.sort()
        for i in range(len(note_presses)):
            note_presses[i]["instrument"] = non_empty_channels.index(note_presses[i]["instrument"])
        print(f"{len(non_empty_channels)} - channels recorded.")

        print("Saving …")

        file = open(out_path, "w")
        file.write(json.dumps(note_presses).replace("},", "},\n"))
        file.close()

        print("Completed!")
        
        #return note_presses



def main(filename: str = ""):

    if filename.find("."): filename = os.path.splitext(filename)[0] # remove extention


    if filename != "":
        in_path = os.path.join(MIDIS_PATH, filename)+".mid"
        out_path = os.path.join(JSONS_PATH, filename)+".json"

        # Check if output file already exists
        if os.path.exists(out_path):
            while True:
                answer = input("Json file for this midi already exists. Do you want to skip this step? [Y/N] ").strip().lower()
                if answer == "j" or answer == "y":
                    with open(out_path, 'r', encoding='utf-8') as file:
                        return json.loads(file.read())
                elif answer == "n": return

        # Find midi files
        if not os.path.exists(in_path): 
            print(f"File {filename.upper()} does not exist!") 
            exit()

        if in_path[-4:] != ".mid":
            midi_files = [file for file in os.listdir(in_path) if file[-4:] == ".mid"]
            midi_files = sorted(midi_files, key=str.lower)
            if (len(midi_files) == 0):
                print(f"Couldn't find a file with extention .mid! Please add mid file in {in_path}")
                input()
                exit()
            else:
                in_path += "/" + filename + ".mid"

        convert(filename)

    else:
        # Find midi files
        midi_files = [file for file in os.listdir(MIDIS_PATH) if file[-4:] == ".mid"]
        midi_files = sorted(midi_files, key=str.lower)
        if (len(midi_files) == 0):
            print(f"Couldn't find a file with extention .mid! Please add mid file in {MIDIS_PATH}")
            input()
            exit()
        
        for file in midi_files:
            if file.find("."): file = os.path.splitext(file)[0] # remove extention
            convert(file)


if __name__ == '__main__':
    main()


































# © SIMON SOVIČ modified by PATRIK GOBEC