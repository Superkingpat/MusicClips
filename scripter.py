import json
import os
import gc
from os import listdir
from os.path import isfile, join
from settings import NOTE_LIST, scripts_path, BATCH_SIZE

def check_script(script, pack_name):
    """
    Checks if all notes in the script exist in the pack, offers transposition if needed.
    
    Args:
        script: List of note dictionaries
        pack_name: Path to the pack directory
        
    Returns:
        The original or transposed script
    """
    if not script:
        raise ValueError("Script is empty")
    if not os.path.exists(pack_name):
        raise FileNotFoundError(f"Pack directory not found: {pack_name}")

    script_notes = {x["note"] for x in script}
    pack_notes = get_pack_notes(pack_name)
    missing_notes = [note for note in script_notes if note not in pack_notes]

    if missing_notes:
        script = handle_missing_notes(script_notes, pack_notes, missing_notes, script, pack_name)

    return script

def get_pack_notes(pack_name):
    """Get sorted list of available notes in the pack"""
    return sort_note_list([
        f.replace(".mp4", "") 
        for f in listdir(pack_name) 
        if isfile(join(pack_name, f)) and f.endswith(".mp4")
    ])

def handle_missing_notes(script_notes, pack_notes, missing_notes, script, pack_name):
    """Handles cases where notes are missing from the pack"""
    sorted_script = sort_note_list(script_notes)
    sorted_pack = sort_note_list(pack_notes)
    
    print(f"Song range: {sorted_script[0]} - {sorted_script[-1]}")
    print(f"Pack range: {sorted_pack[0]} - {sorted_pack[-1]}")
    print(f"Missing notes: {missing_notes}")

    if can_transpose(sorted_script, sorted_pack):
        transposition_value = get_transposition_input(sorted_script, sorted_pack)
        if transposition_value != 0:
            return transpose(transposition_value, script)

def can_transpose(script_notes, pack_notes):
    """Check if transposition is possible"""
    script_range = get_midi_value(script_notes[-1]) - get_midi_value(script_notes[0])
    pack_range = get_midi_value(pack_notes[-1]) - get_midi_value(pack_notes[0])
    return script_range < pack_range

def get_transposition_input(script_notes, pack_notes):
    """Get valid transposition value from user"""
    min_trans = get_midi_value(pack_notes[0]) - get_midi_value(script_notes[0])
    max_trans = get_midi_value(pack_notes[-1]) - get_midi_value(script_notes[-1])
    
    print(f"Possible to transpose. Min: {min_trans}, Max: {max_trans}")
    
    while True:
        try:
            value = int(input("Transposition value [INTEGER] (0 to skip): "))
            if min_trans <= value <= max_trans:
                return value
            print(f"Value must be between {min_trans} and {max_trans}")
        except ValueError:
            print("Please enter a valid integer")

def transpose(num: int, script):
    """Transpose all notes in script by given number of semitones"""
    return [{"note": get_key_code(get_midi_value(x["note"]) + num), **{k:v for k,v in x.items() if k != "note"}} 
            for x in script]

def optimize_script(script, pack_name, output_dir=None):
    """
    Optimizes script by combining simultaneous notes into blocks.
    
    Args:
        script: List of note dictionaries
        pack_name: Path to pack directory
        output_dir: Where to save optimized files (defaults to settings.scripts_path)
        
    Returns:
        tuple: (used_notes, optimized_script, blocks)
    """
    output_dir = output_dir or scripts_path
    os.makedirs(output_dir, exist_ok=True)

    note_list = set()
    new_script = []
    blocks = []
    current_block = None
    note_array = []

    for i, note in enumerate(script):
        if current_block and (note["time"] != current_block["time"] or note["duration"] != current_block["duration"]):
            finalize_block(current_block, new_script, blocks, note_array)
            current_block = None

        if not current_block:
            current_block = {
                "time": note["time"],
                "duration": note["duration"],
                "notes": [note["note"]]
            }
            note_list.add(note["note"])
        else:
            current_block["notes"].append(note["note"])

    if current_block:
        finalize_block(current_block, new_script, blocks, note_array)

    save_optimized_files(output_dir, new_script, blocks)
    return note_list, new_script, blocks

def finalize_block(block, new_script, blocks, note_array):
    """Finalize a block of simultaneous notes"""
    block["notes"] = sort_note_list(block["notes"])
    new_note = {
        "note": block["notes"][0] if len(block["notes"]) == 1 else f"X{len(blocks)}",
        "time": block["time"],
        "duration": block["duration"]
    }
    new_script.append(new_note)
    
    if len(block["notes"]) > 1:
        if block["notes"] in note_array:
            new_note["note"] = f"X{note_array.index(block['notes'])}"
        else:
            note_array.append(block["notes"])
            blocks.append({
                "notes": block["notes"],
                "index": len(blocks),
                "pack_name": block.get("pack_name")
            })

def save_optimized_files(output_dir, new_script, blocks):
    """Save optimized script and blocks to files"""
    with open(os.path.join(output_dir, "optimisedScript.json"), "w") as f:
        json.dump(new_script, f, indent=2)
    
    with open(os.path.join(output_dir, "blocks.json"), "w") as f:
        json.dump(blocks, f, indent=2)

def split_load(script, output_dir=None):
    """
    Splits script into batches for parallel processing.
    
    Args:
        script: List of note dictionaries
        output_dir: Where to save split files (defaults to settings.scripts_path)
        
    Returns:
        tuple: (list of batches, final script)
    """
    output_dir = output_dir or scripts_path
    os.makedirs(output_dir, exist_ok=True)

    batch_size = calculate_batch_size(len(script))
    batches = []
    final_script = []
    
    for i in range(0, len(script), batch_size):
        batch = script[i:i + batch_size]
        batch_number = len(batches)
        
        # Add index to each note in batch
        processed_batch = [{**note, "index": batch_number} for note in batch]
        batches.append(processed_batch)
        
        # Add to final script
        if batch:
            final_script.append({
                "note": f"Y{batch_number}",
                "time": batch[0]["time"]
            })

    save_split_files(output_dir, batches, final_script)
    return batches, final_script

def calculate_batch_size(script_length):
    """Determine optimal batch size based on script length"""
    if script_length < 100:
        return script_length
    return max(1, script_length // BATCH_SIZE)

def save_split_files(output_dir, batches, final_script):
    """Save split script files"""
    with open(os.path.join(output_dir, "splitedScript.json"), "w") as f:
        json.dump(batches, f, indent=2)
    
    with open(os.path.join(output_dir, "final_script.json"), "w") as f:
        json.dump(final_script, f, indent=2)

# Helper functions
def sort_note_list(note_list):
    """Sort notes by their MIDI value"""
    return sorted(note_list, key=get_midi_value)

def get_midi_value(keyCode):
    """Convert note name to MIDI value"""
    if not keyCode or len(keyCode) < 2:
        raise ValueError(f"Invalid note format: {keyCode}")
    return int(keyCode[-1]) * 12 + NOTE_LIST.index(keyCode[:-1])

def get_key_code(midiValue):
    """Convert MIDI value to note name"""
    return NOTE_LIST[midiValue % 12] + str(midiValue // 12)