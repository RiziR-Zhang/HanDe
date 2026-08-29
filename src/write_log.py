import pathlib
from datetime import date, timedelta
import sys
today = date.today()

FILE_PATH = r"D:\myprograms\interest\abc_tracker\logs\log.txt"
print(FILE_PATH)

file = pathlib.Path(FILE_PATH)

with file.open("a") as f:
    f.write(f"{today}\n")
