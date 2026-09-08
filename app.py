import subprocess
import re
import os
import sys
import shutil
import importlib.util
from pathlib import Path

# ============================================================
#  SETTINGS
# ============================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIRMWARE = next(
    (
        str(path)
        for path in (
            Path(ROOT_DIR) / "firmware.bin",
            Path(ROOT_DIR) / "kod" / "firmware.bin",
        )
        if path.is_file()
    ),
    str(Path(ROOT_DIR) / "firmware.bin"),
)
FLASH_OFFSET = "0x0"
COM_SAVE_FILE = os.path.join(ROOT_DIR, "posledni_port.txt")
COPY_SRC = os.path.join(ROOT_DIR, "settings.json")
HOOK_SRC = os.path.join(ROOT_DIR, "notify.py")
CLAUDE_DIR = Path.home() / ".claude"
COPY_DEST = str(CLAUDE_DIR / "settings.json")
CLAUDE_HOOK_DIR = str(CLAUDE_DIR / "hooks")
COPY_DEST_HOOK = os.path.join(CLAUDE_HOOK_DIR, os.path.basename(HOOK_SRC))

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
BOLD = "\033[1m"


def colorize(text, color=None, bold=False):
    if os.name == "nt" and not sys.stdout.isatty():
        return text
    prefix = ""
    if bold:
        prefix += BOLD
    if color:
        prefix += color
    return f"{prefix}{text}{RESET}"


def ask_yes_no(message, default_yes=True):
    try:
        default_label = "Y/n" if default_yes else "y/N"
        answer = input(f"{message} [{default_label}]: ").strip().lower()
    except EOFError:
        print(colorize("No input detected. Using the default option.", YELLOW))
        return default_yes

    if answer == "":
        return default_yes
    return answer in {"y", "yes"}


def ensure_package(module_name, pip_name, description):
    if importlib.util.find_spec(module_name) is not None:
        print(colorize(f"{description} is already installed.", GREEN))
        return True

    print(colorize(f"{description} is missing: {pip_name}", YELLOW))
    print(colorize(f"Installing {pip_name}...", CYAN))
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        print(colorize(f"Installation failed to start: {exc}", RED))
        return False

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        print(colorize(f"Installation failed for {pip_name}.", RED))
        return False

    importlib.invalidate_caches()
    if importlib.util.find_spec(module_name) is not None:
        print(colorize(f"{description} installed successfully.", GREEN))
        return True

    print(colorize(f"The install command finished, but {module_name} is still unavailable.", RED))
    return False


def detect_port_from_output(output):
    if not output:
        return None
    match = re.search(r"(COM\d+)", output, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(ttyUSB\d+|ttyACM\d+)", output, re.IGNORECASE)
    return match.group(1) if match else None


def flash_firmware():
    if not os.path.exists(FIRMWARE):
        print(colorize(f"Firmware file not found: {FIRMWARE}", RED))
        return False

    if not ensure_package("esptool", "esptool", "esptool"):
        print(colorize("Skipping firmware upload because the required library is not available.", YELLOW))
        return False

    command = [
        sys.executable,
        "-m",
        "esptool",
        "--chip",
        "esp32c3",
        "write_flash",
        FLASH_OFFSET,
        FIRMWARE,
    ]

    print(colorize("Searching for ESP32-C3 and flashing the firmware...", BLUE))
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        print(colorize("Firmware upload failed.", RED))
        return False

    port = detect_port_from_output((result.stdout or "") + (result.stderr or ""))
    if port:
        print(colorize(f"Detected port: {port}", GREEN))
        return port

    print(colorize("The upload completed, but the port could not be detected from the output.", YELLOW))
    return None


def save_port(port):
    try:
        with open(COM_SAVE_FILE, "w", encoding="utf-8") as file:
            file.write(port)
        print(colorize(f"Saved last port to: {COM_SAVE_FILE}", GREEN))
    except Exception as exc:
        print(colorize(f"Could not save the port: {exc}", RED))


def copy_files():
    missing_files = [path for path in (COPY_SRC, HOOK_SRC) if not os.path.exists(path)]
    if missing_files:
        for path in missing_files:
            print(colorize(f"Source file not found: {path}", RED))
        return False

    try:
        os.makedirs(os.path.dirname(COPY_DEST), exist_ok=True)
        shutil.copy2(COPY_SRC, COPY_DEST)

        os.makedirs(CLAUDE_HOOK_DIR, exist_ok=True)
        shutil.copy2(HOOK_SRC, COPY_DEST_HOOK)

        print(colorize("Files copied successfully.", GREEN))
        return True
    except Exception as exc:
        print(colorize(f"Copy failed: {exc}", RED))
        return False


def main():
    print(colorize("========================================", BLUE))
    print(colorize("ESP32-C3 Firmware Update Tool", BOLD + BLUE))
    print(colorize("========================================", BLUE))

    port = flash_firmware()
    if port:
        save_port(port)
    else:
        print(colorize("Continuing to the next step without a detected port.", YELLOW))

    copy_files()
    print(colorize("Process finished successfully.", GREEN))


if __name__ == "__main__":
    main()