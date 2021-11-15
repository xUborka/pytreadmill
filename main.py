import sys
import io
import cProfile
import pstats
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from widgets.main_window import Window

def start_pr_timer(application, argv):
    timer = QTimer()
    timer.setSingleShot(True)
    timer.setInterval(int(argv[2]) * 1000)
    timer.timeout.connect(application.exit)
    timer.start()
    return timer

def finish_profiling(prof):
    prof_stream = io.StringIO()
    prof_stat = pstats.Stats(prof, stream=prof_stream).sort_stats('name')
    prof_stat.print_stats()

    date = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = "profile-stat_" + date + ".csv"

    with open(filename, 'w+') as output_file:
        prof_stream.seek(0)
        for i in range(4):
            prof_stream.readline()
        for line in prof_stream:
            listed_line = line.split(sep=None, maxsplit=5)
            line_to_write = ','.join(listed_line)
            output_file.write(line_to_write)
        # output_file.write(prof_stream.getvalue())
    
    print("({}) {} saved in working directory.\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), filename))

if len(sys.argv) == 3 and __name__ == "__main__":
    if sys.argv[1] == "profiler" and sys.argv[2].isnumeric():
        pr = cProfile.Profile()
        pr.enable()

        app = QApplication(sys.argv)
        Gui = Window()
        if sys.argv[2] != 0:
            pr_timer = start_pr_timer(app, sys.argv)
            print("({}) Application started in profiling mode. Application will close in {} seconds.\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), sys.argv[2]))
        else:
            print("({}) Application started in profiling mode. Profiling will finish only when user closes the application.".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        exit_code = app.exec_()

        pr.disable()
        finish_profiling(pr)

        sys.exit(exit_code)
elif __name__ == "__main__":
    app = QApplication(sys.argv)
    Gui = Window()
    sys.exit(app.exec_())
