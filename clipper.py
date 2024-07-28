import json
import gc
from settings import *
from renderer import *
from scripter import *


def main(filename: str):
    gc.enable()

    script = json.load(open(JSONS_PATH+"/"+filename+".json"))

    script = checkScript(script, PACK_NAME)

    _, script, blocks = optimizeScript(script, PACK_NAME)

    script_list, final_script = splitLoad(script)

    renderBlockClips(BATCH_SIZE, blocks)

    renderScriptClips(BATCH_SIZE, script_list)

    renderFinal(final_script)

if __name__ == '__main__':
    main()