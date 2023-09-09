import os
import json
from math import floor
from typing import no_type_check_decorator

try:
    from mido import MidiFile
except ImportError:
    print("Modula 'mido' ni bilo mogoče uvoziti. Nameščam...")
    os.system('cmd /c "pip install mido"')
    from mido import MidiFile


input_path = "./data"
output_path = "./data/music.json"
channel_filter = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ]
note_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
minimum_start_delay = 2 # [s]


def main():
    global input_path, output_path, channel_filter, note_list, minimum_start_delay

    # Check if output file already exists
    if os.path.exists(output_path):
        while True:
            answer = input("Json datoteka že obstaja (ne nujno od te pesmi). Ali želite preskočiti ta korak? [j/n] ").strip().lower()
            if answer == "j" or answer == "y":
                with open(output_path, 'r', encoding='utf-8') as file:
                    return json.loads(file.read())
            elif answer == "n": break

    # Find midi files
    if input_path[-4:] != ".mid":
        midi_files = [file for file in os.listdir(input_path) if file[-4:] == ".mid"]
        midi_files = sorted(midi_files, key=str.lower)
        if (len(midi_files) == 0):
            print(f"V dani mapi ni nobene datoteke s končnico .mid! Dajte pesem v mapo {input_path}")
            input()
            exit()
        else:
            input_path += "/" + midi_files[0]

    # Construct note actions out of the midi data
    midi_note_actions = []
    for message in MidiFile(input_path).play():
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
                note = note_list[note_index % 12] + str(floor(note_index / 12) - 1)
            elif element[:4] == "time": time = float(element.split("=")[1])
        if channel not in channel_filter or state == None or note == None or time == None: continue
        
        if len(midi_note_actions) > 0: time += midi_note_actions[-1]["time"]
        
        midi_note_actions.append({ "state":state, "note":note, "channel":channel, "time":time })

        print(midi_note_actions[-1])
        
    
    # convert { true, C1, time = 1.5 } and { false, C1, time = 2.5 } to { C1, time = 1.5, duration = 1 }
    print("Pretvarjam …")
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

    '''
    print(f" Note presses: {len(note_presses)}    Midi note actions: {len(midi_note_actions)}")

    fc, tc = 0, 0
    for a in midi_note_actions:
        if a["state"]: tc += 1
        else: fc += 1

    print(f" False counter: {fc}    True counter: {tc}")
    exit()'''

    # Add start delay if necessary
    if note_presses[0]["time"] < minimum_start_delay:
        time_shift = minimum_start_delay - note_presses[0]["time"]
        print(f"Zamikam čas pritiskov not za {time_shift}s …")
        for note_press in note_presses:
            note_press["time"] += time_shift
    
    # Sort notes that start at the same time by channel in descending order
    """print("Sortiram …")
    t_end = note_presses[-1]["time"]
    note_presses.sort(key=lambda press: (t_end-press["time"], press["instrument"]), reverse=True)"""

    # Compress channel numbering
    print("Stiskam kanale …")
    non_empty_channels = []
    for note_press in note_presses:
        if note_press["instrument"] not in non_empty_channels:
            non_empty_channels.append(note_press["instrument"])
    non_empty_channels.sort()
    for i in range(len(note_presses)):
        note_presses[i]["instrument"] = non_empty_channels.index(note_presses[i]["instrument"])
    print(f"OBSTAJA {len(non_empty_channels)} BARVNIH KANALOV.")

    print("Shranjujem …")

    file = open(output_path, "w")
    file.write(json.dumps(note_presses).replace("},", "},\n"))
    file.close()

    print("KONČAL!")
    
    return note_presses


if __name__ == '__main__':
    main()


































# © SIMON SOVIČ modified by PATRIK GOBEC