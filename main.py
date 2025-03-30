import mid_to_json_converter as mTj
import clipper as c
from organizer import createMainLayout
import cProfile
import pstats
import io
from pstats import SortKey
import coverage

def main():
    filename = "FireworksMIDI"

    cov = coverage.Coverage()
    cov.start()

    pr = cProfile.Profile()
    pr.enable()

    mTj.main(filename)
    path = createMainLayout(filename)
    c.main(path, filename)

    pr.disable()

    cov.stop()
    cov.save()
    cov.report()
    cov.html_report(directory="coverage_report") 
    cov.xml_report(outfile="coverage.xml")

    clip_profile = io.StringIO()
    ps = pstats.Stats(pr, stream=clip_profile).sort_stats(SortKey.CUMULATIVE)
    ps.print_stats()
    with open('clipping_profile.txt', 'w') as f:
        f.write(clip_profile.getvalue())

if __name__ == '__main__':
    main()
