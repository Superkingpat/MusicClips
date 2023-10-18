import moviepy.editor as mp
from os.path import isdir

FULL_HD = (1920, 1080)

def main(presses: list[dict]):
    # Ask for pack name
    pack_name = './无效名称'
    while not isdir(pack_name):
        pack_name = './data/packs/' + input('Ime paketa: ')

    # Ask for split template name
    split_template_name = '模板名称无效'
    while split_template_name not in SPLIT_TEMPLATE_NAMES.keys():
        split_template_name = input(f'Ime razdelitvene predloge ({",".join(SPLIT_TEMPLATE_NAMES.keys())}):')
    split_template = SPLIT_TEMPLATE_NAMES[split_template_name]
    
    video = mp.CompositeVideoClip(size=FULL_HD)


def vertical(composite: mp.CompositeVideoClip, video_clips: list[mp.VideoClip]) -> mp.VideoClip:
    pass

def horizontal(composite: mp.CompositeVideoClip, video_clips: list[mp.VideoClip]) -> mp.VideoClip:
    pass


SPLIT_TEMPLATE_NAMES = {
    'vertical': vertical,
    'horizontal': horizontal,
}