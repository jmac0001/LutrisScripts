#!/usr/bin/env python3
"""
write_fxfight_cfg.py

Generates the FXFIGHT.CFG configuration file.

This script replaces the need to run SETUP.EXE when the desired
configuration is already known.
"""

from pathlib import Path
import argparse
import sys


def Generate_Config(
    InstallDirectory: str,
    CdDrive: str,
    Language: int,
    SoundCard: int,
) -> str:

    return f"""CD PATH={CdDrive}
HD PATH={InstallDirectory}

LANGUAGE={Language}
SOUND CARD={SoundCard}

NONE BASE ADDRESS=-1
NONE IRQ1=-1
NONE IRQ2=-1
NONE DMA1=-1
NONE DMA2=-1

SOUND BLASTER / COMPATIBLE BASE ADDRESS=544
SOUND BLASTER / COMPATIBLE IRQ1=7
SOUND BLASTER / COMPATIBLE IRQ2=-1
SOUND BLASTER / COMPATIBLE DMA1=1
SOUND BLASTER / COMPATIBLE DMA2=-1

SOUND BLASTER PRO BASE ADDRESS=544
SOUND BLASTER PRO IRQ1=5
SOUND BLASTER PRO IRQ2=-1
SOUND BLASTER PRO DMA1=1
SOUND BLASTER PRO DMA2=-1

SOUND BLASTER 16 BASE ADDRESS=544
SOUND BLASTER 16 IRQ1=7
SOUND BLASTER 16 IRQ2=-1
SOUND BLASTER 16 DMA1=1
SOUND BLASTER 16 DMA2=5

GRAVIS ULTRASOUND BASE ADDRESS=544
GRAVIS ULTRASOUND IRQ1=5
GRAVIS ULTRASOUND IRQ2=5
GRAVIS ULTRASOUND DMA1=3
GRAVIS ULTRASOUND DMA2=3
"""


def Main() -> int:

    Parser = argparse.ArgumentParser(
        description="Generate FXFIGHT.CFG"
    )

    Parser.add_argument(
        "--output",
        required=True,
        help="Output FXFIGHT.CFG path"
    )

    Parser.add_argument(
        "--install-dir",
        default=r"C:\FXFIGHT",
        help="DOS install directory"
    )

    Parser.add_argument(
        "--cd-drive",
        default="D:",
        help="DOS CD drive"
    )

    Parser.add_argument(
        "--language",
        type=int,
        default=0,
        help="Language number"
    )

    Parser.add_argument(
        "--sound-card",
        type=int,
        default=1,
        help="Sound card index (1 = Sound Blaster)"
    )

    Args = Parser.parse_args()

    OutputPath = Path(Args.output)

    OutputPath.parent.mkdir(parents=True, exist_ok=True)

    OutputPath.write_text(
        Generate_Config(
            InstallDirectory=Args.install_dir,
            CdDrive=Args.cd_drive,
            Language=Args.language,
            SoundCard=Args.sound_card,
        ),
        encoding="ascii",
        newline="\r\n",
    )

    print(f"Wrote {OutputPath}")

    return 0


if __name__ == "__main__":
    sys.exit(Main())