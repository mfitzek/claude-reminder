import sys
import subprocess
import importlib.util

# ============================================================
#  NASTAVENÍ
# ============================================================

BAUDRATE = 115200

# Klíčová slova v popisu USB-sériového čipu, podle kterých se pozná ESP32-C3
KLICOVA_SLOVA = ["cp210", "ch340", "usb-serial", "usb serial", "silicon labs", "wch"]

# ============================================================


def zajisti_pyserial():
    """Zkontroluje, jestli je pyserial nainstalovaný, a pokud ne, rovnou (bez ptaní) ho doinstaluje.
    Appka běží mimo dohled uživatele, takže žádné interaktivní dotazy."""
    if importlib.util.find_spec("serial") is not None:
        return

    vysledek = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyserial"],
        capture_output=True, text=True,
    )
    if vysledek.returncode != 0:
        print("CHYBA: Instalace pyserial selhala.")
        print(vysledek.stderr)
        sys.exit(1)


def najdi_port():
    from serial.tools import list_ports

    porty = list(list_ports.comports())
    if not porty:
        return None

    for p in porty:
        popis = (p.description or "").lower()
        if any(klic in popis for klic in KLICOVA_SLOVA):
            return p.device

    # pokud je připojený jen jeden port, vzít ten
    if len(porty) == 1:
        return porty[0].device

    return None


def posli_jednicku(port):
    import serial
    import time  

    with serial.Serial(port, BAUDRATE, timeout=1) as ser:
        
        ser.write(b"1")
        time.sleep(1)

def main():
    zajisti_pyserial()

    port = najdi_port()
    if not port:
        print("ESP32-C3 nebyla nalezena na žádném COM portu. Zkontroluj připojení.")
        sys.exit(1)

    print(f"Nalezen port: {port}")
    posli_jednicku(port)
    print("Hotovo.")


if __name__ == "__main__":
    main()