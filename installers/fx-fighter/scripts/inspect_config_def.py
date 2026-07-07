#!/usr/bin/env python3
"""
inspect_config_def.py

Reads and displays known configuration values from a FX Fighter CONFIG.DEF file.

Currently decodes:
    - Player 1 keyboard mappings

Future enhancements:
    - Player 2 mappings
    - Joystick mappings
    - Difficulty
    - Video options
    - Unknown bytes
"""

from pathlib import Path
import argparse
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONTROL_OFFSET = 0x13
CONTROL_COUNT = 6

CONTROL_NAMES = (
    "Attack",
    "Retreat",
    "Jump",
    "Duck",
    "Punch",
    "Kick",
)

# IBM PC / DOS Set 1 keyboard scan codes
SCAN_CODES = {
    0x01: "Esc",

    0x02: "1",
    0x03: "2",
    0x04: "3",
    0x05: "4",
    0x06: "5",
    0x07: "6",
    0x08: "7",
    0x09: "8",
    0x0A: "9",
    0x0B: "0",

    0x0C: "-",
    0x0D: "=",
    0x0E: "Backspace",
    0x0F: "Tab",

    0x10: "Q",
    0x11: "W",
    0x12: "E",
    0x13: "R",
    0x14: "T",
    0x15: "Y",
    0x16: "U",
    0x17: "I",
    0x18: "O",
    0x19: "P",

    0x1A: "[",
    0x1B: "]",
    0x1C: "Enter",
    0x1D: "Left Ctrl",

    0x1E: "A",
    0x1F: "S",
    0x20: "D",
    0x21: "F",
    0x22: "G",
    0x23: "H",
    0x24: "J",
    0x25: "K",
    0x26: "L",

    0x27: ";",
    0x28: "'",
    0x29: "`",

    0x2A: "Left Shift",

    0x2B: "\\",

    0x2C: "Z",
    0x2D: "X",
    0x2E: "C",
    0x2F: "V",
    0x30: "B",
    0x31: "N",
    0x32: "M",

    0x33: ",",
    0x34: ".",
    0x35: "/",

    0x36: "Right Shift",

    0x37: "Keypad *",
    0x38: "Left Alt",
    0x39: "Space",

    0x3B: "F1",
    0x3C: "F2",
    0x3D: "F3",
    0x3E: "F4",
    0x3F: "F5",
    0x40: "F6",
    0x41: "F7",
    0x42: "F8",
    0x43: "F9",
    0x44: "F10",
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def Read_Config(ConfigPath: Path) -> bytearray:
    """Reads the CONFIG.DEF file."""

    if not ConfigPath.exists():
        raise FileNotFoundError(ConfigPath)

    return bytearray(ConfigPath.read_bytes())


def Decode_Key(ScanCode: int) -> str:
    """Returns a readable key name."""

    return SCAN_CODES.get(
        ScanCode,
        f"Unknown (0x{ScanCode:02X})"
    )


def Print_Player1_Controls(Data: bytearray) -> None:
    """Displays Player 1 controls."""

    print("Player 1 Controls")
    print("-----------------")

    for Index, ControlName in enumerate(CONTROL_NAMES):

        ScanCode = Data[CONTROL_OFFSET + Index]

        print(
            f"{ControlName:<10}"
            f"{Decode_Key(ScanCode):<15}"
            f"(0x{ScanCode:02X})"
        )


def Print_Hex_Dump(Data: bytearray) -> None:
    """Displays the control bytes."""

    print()
    print("Raw Control Bytes")
    print("-----------------")

    Offset = CONTROL_OFFSET

    Values = " ".join(
        f"{Value:02X}"
        for Value in Data[Offset:Offset + CONTROL_COUNT]
    )

    print(f"Offset 0x{Offset:02X}: {Values}")


def Main() -> int:

    Parser = argparse.ArgumentParser(
        description="Inspect a FX Fighter CONFIG.DEF file."
    )

    Parser.add_argument(
        "ConfigFile",
        help="Path to CONFIG.DEF"
    )

    Args = Parser.parse_args()

    ConfigPath = Path(Args.ConfigFile)

    try:
        Data = Read_Config(ConfigPath)

    except Exception as Ex:
        print(f"ERROR: {Ex}")
        return 1

    print()
    print("FX Fighter CONFIG.DEF Inspector")
    print("=" * 40)
    print(f"File : {ConfigPath}")
    print(f"Size : {len(Data)} bytes")
    print()

    Print_Player1_Controls(Data)
    Print_Hex_Dump(Data)

    return 0


if __name__ == "__main__":
    sys.exit(Main())
