#!/usr/bin/env python3
"""
patch_fxfighter_config.py

Patches FX Fighter CONFIG.DEF keyboard controls.

Known CONFIG.DEF layout:
    Offset 0x13 through 0x18:
        Attack, Retreat, Jump, Duck, Punch, Kick

Values are IBM PC / DOS Set 1 keyboard scan codes.
"""

from pathlib import Path
import argparse
import shutil
import sys


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

LAYOUTS = {
    "original": bytes([
        0x2E,  # Attack  = C
        0x2D,  # Retreat = X
        0x1E,  # Jump    = A
        0x2C,  # Duck    = Z
        0x2F,  # Punch   = V
        0x10,  # Kick    = Q
    ]),

    "modern": bytes([
        0x20,  # Attack  = D
        0x1E,  # Retreat = A
        0x11,  # Jump    = W
        0x1F,  # Duck    = S
        0x24,  # Punch   = J
        0x25,  # Kick    = K
    ]),

    "r36s": bytes([
        0x20,  # Attack  = D
        0x1E,  # Retreat = A
        0x11,  # Jump    = W
        0x1F,  # Duck    = S
        0x24,  # Punch   = J
        0x25,  # Kick    = K
    ]),
}

SCAN_CODE_NAMES = {
    0x10: "Q",
    0x11: "W",
    0x1E: "A",
    0x1F: "S",
    0x20: "D",
    0x24: "J",
    0x25: "K",
    0x2C: "Z",
    0x2D: "X",
    0x2E: "C",
    0x2F: "V",
}


def Get_Key_Name(ScanCode: int) -> str:
    return SCAN_CODE_NAMES.get(ScanCode, f"Unknown 0x{ScanCode:02X}")


def Validate_Config(Data: bytearray, ConfigPath: Path) -> None:
    if len(Data) < CONTROL_OFFSET + CONTROL_COUNT:
        raise ValueError(f"{ConfigPath} is too small to be a valid CONFIG.DEF file.")


def Backup_Config(ConfigPath: Path) -> Path:
    BackupPath = ConfigPath.with_suffix(ConfigPath.suffix + ".bak")

    if not BackupPath.exists():
        shutil.copy2(ConfigPath, BackupPath)

    return BackupPath


def Print_Layout(LayoutName: str, LayoutBytes: bytes) -> None:
    print()
    print(f"Applied layout: {LayoutName}")
    print("----------------------")

    for ControlName, ScanCode in zip(CONTROL_NAMES, LayoutBytes):
        print(f"{ControlName:<10}: {Get_Key_Name(ScanCode):<10} 0x{ScanCode:02X}")


def Patch_Config(ConfigPath: Path, LayoutName: str, CreateBackup: bool = True) -> None:
    if LayoutName not in LAYOUTS:
        ValidLayouts = ", ".join(sorted(LAYOUTS.keys()))
        raise ValueError(f"Unknown layout '{LayoutName}'. Valid layouts: {ValidLayouts}")

    if not ConfigPath.exists():
        raise FileNotFoundError(f"File not found: {ConfigPath}")

    Data = bytearray(ConfigPath.read_bytes())
    Validate_Config(Data, ConfigPath)

    BackupPath = None

    if CreateBackup:
        BackupPath = Backup_Config(ConfigPath)

    LayoutBytes = LAYOUTS[LayoutName]
    Data[CONTROL_OFFSET:CONTROL_OFFSET + CONTROL_COUNT] = LayoutBytes
    ConfigPath.write_bytes(Data)

    print(f"Patched: {ConfigPath}")

    if BackupPath:
        print(f"Backup : {BackupPath}")

    Print_Layout(LayoutName, LayoutBytes)


def Main() -> int:
    Parser = argparse.ArgumentParser(
        description="Patch FX Fighter CONFIG.DEF keyboard controls."
    )

    Parser.add_argument(
        "ConfigFile",
        help="Path to CONFIG.DEF"
    )

    Parser.add_argument(
        "--layout",
        choices=sorted(LAYOUTS.keys()),
        default="modern",
        help="Control layout to apply. Default: modern"
    )

    Parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create CONFIG.DEF.bak"
    )

    Args = Parser.parse_args()

    try:
        Patch_Config(
            ConfigPath=Path(Args.ConfigFile),
            LayoutName=Args.layout,
            CreateBackup=not Args.no_backup,
        )

    except Exception as Ex:
        print(f"ERROR: {Ex}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(Main())