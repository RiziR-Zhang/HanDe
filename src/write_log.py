import pathlib
from datetime import date, timedelta
import sys
today = date.today()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE_PATH = PROJECT_ROOT / "logs" / "log.txt"
print(FILE_PATH)

file = FILE_PATH

with file.open("a") as f:
    f.write(f"{today}\n")
