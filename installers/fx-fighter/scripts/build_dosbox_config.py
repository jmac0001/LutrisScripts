#!/usr/bin/env python3
"""
build_dosbox_config.py

Generates a DOSBox configuration file for FX Fighter.
"""

from pathlib import Path
import argparse
import sys


DEFAULT_OUTPUT = "dosbox.conf"


def Build_Config(
    InstallRoot: Path,
    CuePath: Path,
    OutputPath: Path,
    Cycles: int,
    Fullscreen: bool,
    GameDirName: str,
    GameExe: str,
) -> str:

    FullscreenValue = "true" if Fullscreen else "false"

    return f"""[sdl]
fullscreen={FullscreenValue}
fulldouble=true
fullresolution=desktop
windowresolution=1280x960
output=opengl

[render]
aspect=true
scaler=normal3x

[dosbox]
machine=svga_s3
memsize=16

[cpu]
core=dynamic
cputype=auto
cycles=fixed {Cycles}
cycleup=1000
cycledown=1000

[mixer]
rate=44100
blocksize=1024
prebuffer=25

[sblaster]
sbtype=sb16
sbbase=220
irq=7
dma=1
hdma=5
oplmode=auto
oplemu=default
oplrate=44100

[autoexec]
@echo off
SET BLASTER=A220 I7 D1 H5 T6
mount c "{InstallRoot}"
imgmount d "{CuePath}" -t iso
c:
cd \\{GameDirName}
{GameExe}
exit
"""


def Validate_Path(PathToCheck: Path, Description: str, MustExist: bool = True) -> None:
    if MustExist and not PathToCheck.exists():
        raise FileNotFoundError(f"{Description} does not exist: {PathToCheck}")


def Main() -> int:
    Parser = argparse.ArgumentParser(
        description="Generate a DOSBox config for FX Fighter."
    )

    Parser.add_argument(
        "--install-root",
        required=True,
        help="DOSBox C: mount root, for example /tmp/dosgames"
    )

    Parser.add_argument(
        "--cue",
        required=True,
        help="Path to FX Fighter .cue file"
    )

    Parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output config path. Default: {DEFAULT_OUTPUT}"
    )

    Parser.add_argument(
        "--cycles",
        type=int,
        default=32000,
        help="Fixed DOSBox CPU cycles. Default: 32000"
    )

    Parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Enable fullscreen"
    )

    Parser.add_argument(
        "--game-dir",
        default="FXFIGHT",
        help="Installed game directory under the DOSBox C: root. Default: FXFIGHT"
    )

    Parser.add_argument(
        "--game-exe",
        default="FIGHT.EXE",
        help="Game executable. Default: FIGHT.EXE"
    )

    Args = Parser.parse_args()

    InstallRoot = Path(Args.install_root).expanduser().resolve()
    CuePath = Path(Args.cue).expanduser().resolve()
    OutputPath = Path(Args.output).expanduser().resolve()

    try:
        Validate_Path(InstallRoot, "Install root")
        Validate_Path(CuePath, "CUE file")

        ConfigText = Build_Config(
            InstallRoot=InstallRoot,
            CuePath=CuePath,
            OutputPath=OutputPath,
            Cycles=Args.cycles,
            Fullscreen=Args.fullscreen,
            GameDirName=Args.game_dir,
            GameExe=Args.game_exe,
        )

        OutputPath.parent.mkdir(parents=True, exist_ok=True)
        OutputPath.write_text(
            ConfigText,
            encoding="utf-8",
            newline="\r\n",
        )

        print(f"Wrote DOSBox config: {OutputPath}")

    except Exception as Ex:
        print(f"ERROR: {Ex}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(Main())