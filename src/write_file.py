import pathlib
# import os
from datetime import date, timedelta
import sys
today = date.today()
# print(today)
# print(sys.argv)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKIN_PATH_FILE = PROJECT_ROOT / "checkin_path.txt"
DEFAULT_CHECKIN_PATH = r"D:\vardocs\MyObsidian\Sched\ABC.md"  # keep in sync with setup.py

FILE_PATH = DEFAULT_CHECKIN_PATH
if CHECKIN_PATH_FILE.exists():
    cfg = CHECKIN_PATH_FILE.read_text(encoding="utf-8").strip()
    if cfg:
        FILE_PATH = cfg
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
