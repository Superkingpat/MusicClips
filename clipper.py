import json
import gc
from settings import *
from renderer import *
from scripter import *


def main(filename = ""):
    gc.enable()

    script = json.load(open(r'./data/jsons/Autumnbreeze.json'))
    
    pack_name = './data/packs/' +  "PianoTestPack"#input('Ime paketa: ')

    script = checkScript(script, pack_name)

    _, script, blocks = optimizeScript(script, pack_name)

    script_list, final_script = splitLoad(script)

    renderBlockClips(BATCH_SIZE, blocks)

    renderScriptClips(BATCH_SIZE, script_list)

    renderFinal(final_script)

if __name__ == '__main__':
    main()