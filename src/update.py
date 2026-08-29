import pathlib
from datetime import date
import os
import subprocess
import sys
LOG_PATH = r"D:\myprograms\interest\abc_tracker\logs\log.txt"
CHAR_PER_LINE = 10 + 16 + 2

def today_has_bad_record():
    today = date.today()
    file = pathlib.Path(LOG_PATH)
    bad_record = False
    with file.open("r") as f:
        log_size = f.seek(0, os.SEEK_END)
        last_line_pos = max(0, log_size - CHAR_PER_LINE)
        f.seek(last_line_pos, os.SEEK_SET)
        last_line = f.read(CHAR_PER_LINE)
        # print(f" '{str(today)}' vs '{last_line}'", file=sys.stderr)
        if str(today) in last_line:
            bad_record = True
    with file.open("a") as f:
        if bad_record:
            f.write(f"{today}'s record broken\n")
            # print(f"{today}'s record broken\n", file=sys.stderr)
        else:
            f.write(f"{today}'s record kept\n")
            # print(f"{today}'s record kept\n", file=sys.stderr)
    return bad_record

if not today_has_bad_record():
    subprocess.run(["pythonw", r"D:\myprograms\interest\abc_tracker\write_file.py", "--mark"])