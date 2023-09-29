import mid_to_json_converter as mTj
import clipper as c
from organizer import createMainLayout


if __name__ == '__main__':
    filename = "FireworksMIDI"

    #mTj.main(filename)

    createMainLayout(filename)

    c.main(filename)