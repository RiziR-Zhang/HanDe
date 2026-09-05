#!/usr/bin/env python
r"""One-time Windows bootstrap for abc_tracker.

Prompts for the check-in note path, then creates:
  1. A Task Scheduler event: runs `pythonw <repo>\src\update.py` daily at 23:55
     (interactive, current user; normally needs no admin).
  2. A Desktop shortcut: runs `pythonw <repo>\src\write_log.py` (manual "broken" day).

Run:  python src/setup.py

Stdlib only. Windows-specific behaviour lives in the functions below, so a
future macOS/Linux port replaces those functions, not main().
"""
import ctypes
import pathlib
import shutil
import subprocess
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
LOG_DIR = PROJECT_ROOT / "logs"
UPDATE_SCRIPT = SRC_DIR / "update.py"
WRITE_LOG_SCRIPT = SRC_DIR / "write_log.py"
CHECKIN_PATH_FILE = PROJECT_ROOT / "checkin_path.txt"
DEFAULT_CHECKIN_PATH = r"D:\vardocs\MyObsidian\Sched\ABC.md"  # keep in sync with write_file.py

TASK_NAME = "abc_tracker_update"
SHORTCUT_NAME = "abc_tracker.lnk"
DAILY_TIME = "23:55"

ELEVATED = "--elevated" in sys.argv
CREATE_NO_WINDOW = 0x08000000  # no console flash even if run via pythonw


# ---------------------------------------------------------------------------
# Platform-neutral helpers
# ---------------------------------------------------------------------------

def run(args):
    """Run a command, capturing output decoded in the ANSI codepage (mbcs)."""
    p = subprocess.run(args, capture_output=True, creationflags=CREATE_NO_WINDOW)
    return p.returncode, p.stdout.decode("mbcs", "replace"), p.stderr.decode("mbcs", "replace")


def console_python():
    """An executable that shows a console (python.exe, not pythonw.exe)."""
    exe = pathlib.Path(sys.executable)
    if exe.name.lower() == "pythonw.exe":
        sibling = exe.with_name("python.exe")
        if sibling.exists():
            return str(sibling)
    return sys.executable


# ---------------------------------------------------------------------------
# Windows-specific
# ---------------------------------------------------------------------------

def access_denied_text():
    """OS-localized 'Access is denied.' for error 5 (e.g. '拒绝访问。')."""
    FROM_SYSTEM, IGNORE_INSERTS = 0x00001000, 0x00000200
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.kernel32.FormatMessageW(FROM_SYSTEM | IGNORE_INSERTS, None, 5, 0,
                                          buf, len(buf), None)
    return buf.value.strip()


def relaunch_elevated():
    """Re-run this script as administrator; the UAC prompt appears here."""
    script = pathlib.Path(__file__).resolve()
    rc = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", console_python(), f'"{script}" --elevated', None, 1)
    return rc > 32  # e.g. 1223 = ERROR_CANCELLED


def create_task():
    """Register the daily 23:55 task; absolute paths inside /TR."""
    pythonw = shutil.which("pythonw")
    tr = f'"{pythonw}" "{UPDATE_SCRIPT}"'  # inner quotes stored verbatim in the task
    args = ["schtasks", "/Create", "/TN", TASK_NAME,
            "/TR", tr, "/SC", "DAILY", "/ST", DAILY_TIME, "/F"]
    code, out, err = run(args)
    if code == 0:
        print(f"计划任务 '{TASK_NAME}' 已创建：每天 {DAILY_TIME}。")
        return True
    # schtasks exits 1 for every error, so detect access-denied via stderr text.
    if not ELEVATED and (access_denied_text() in err
                         or "access is denied" in err.lower()):
        print("创建计划任务需要管理员权限，正在申请提权...")
        if relaunch_elevated():
            sys.exit(0)  # the elevated child redoes the work; parent hands off
        print("提权被取消（UAC 未授权），计划任务未创建。")
        return False
    print(f"创建计划任务 '{TASK_NAME}' 失败：{err.strip() or out.strip() or code}")
    return False


def ps_lit(s):
    """Quote a Python string as a PowerShell single-quoted literal."""
    return "'" + s.replace("'", "''") + "'"


def create_shortcut():
    """Desktop .lnk via PowerShell WScript.Shell COM; absolute paths inside."""
    pythonw = shutil.which("pythonw")
    args_val = '"' + str(WRITE_LOG_SCRIPT) + '"'  # .lnk Arguments value
    ps_cmd = (
        "$ws = New-Object -ComObject WScript.Shell; "
        "$d = [Environment]::GetFolderPath('Desktop'); "  # OneDrive-safe
        "$s = $ws.CreateShortcut($d + '\\" + SHORTCUT_NAME + "'); "
        f"$s.TargetPath = {ps_lit(pythonw)}; "
        f"$s.Arguments = {ps_lit(args_val)}; "
        f"$s.WorkingDirectory = {ps_lit(str(PROJECT_ROOT))}; "
        "$s.Save(); "
        "Write-Output ($d + '\\" + SHORTCUT_NAME + "')"
    )
    code, out, err = run(["powershell.exe", "-NoProfile", "-Command", ps_cmd])
    if code == 0:
        print("桌面快捷方式已创建：", out.strip())
        return True
    print("创建桌面快捷方式失败：", err.strip() or out.strip())
    return False


# ---------------------------------------------------------------------------
# Interaction (skipped when re-running elevated)
# ---------------------------------------------------------------------------

def ask_checkin_path():
    """Ask for the check-in note path, then persist it to checkin_path.txt."""
    current = (CHECKIN_PATH_FILE.read_text(encoding="utf-8").strip()
               if CHECKIN_PATH_FILE.exists() else DEFAULT_CHECKIN_PATH)
    try:
        user = input(f"打卡文件位置（Obsidian 笔记，回车使用 {current}）: ").strip()
    except EOFError:  # piped input; use the default
        user = ""
    if user:
        path = pathlib.Path(user).expanduser()
        if not path.is_absolute():
            path = pathlib.Path.cwd() / path
    else:
        path = pathlib.Path(current)
    if not path.parent.exists():
        print(f"警告：目录不存在 {path.parent}，write_file.py 追加时会失败")
    CHECKIN_PATH_FILE.write_text(str(path), encoding="utf-8")
    return path


def main():
    if sys.platform != "win32":
        print("错误：此脚本仅支持 Windows。")
        return 1
    if not shutil.which("pythonw"):
        print("错误：PATH 中找不到 'pythonw'（应位于 python.exe 旁）。")
        return 1
    LOG_DIR.mkdir(parents=True, exist_ok=True)  # both scripts append here
    if not ELEVATED:
        ask_checkin_path()
    ok = create_shortcut()  # never needs admin
    if not create_task():
        ok = False
    if ok:
        print("配置完成。计划任务每天 23:55 运行；桌面已建快捷方式。")
        print(f"验证：schtasks /Query /TN {TASK_NAME}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
