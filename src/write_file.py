import pathlib
# import os
from datetime import date, timedelta
import sys
today = date.today()
# print(today)
# print(sys.argv)

FILE_PATH = r"D:\vardocs\MyObsidian\Sched\ABC.md"
# print(FILE_PATH)

file = pathlib.Path(FILE_PATH)

if sys.argv[1] == "--mark":
    with file.open("a") as f:
        f.write(f"\n* {today} - 2")
elif sys.argv[1] == "--last":
    days_ago = today - timedelta(days=int(sys.argv[2]))
    with file.open("a") as f:
        f.write(f"\n* {days_ago} - 2")
else:
    pass
