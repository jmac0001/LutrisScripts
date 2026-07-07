#!/usr/bin/env python3
"""
install_fxfighter.py

Installs FX Fighter from either:
  1. A mounted CD/ISO directory via --source
  2. A retail .cue/.bin image via --cue

For --cue mode:
  - Converts the CUE/BIN to a temporary ISO using bchunk
  - Mounts the temporary ISO using fuseiso
  - Copies game files
  - Generates FXFIGHT.CFG
  - Generates dosbox.conf
  - Cleans up the temporary mount
"""

from pathlib import Path
import argparse
import shutil
import subprocess
import sys
import tempfile


REQUIRED_ITEMS = [
    "dos4gw.exe",
    "fight.exe",
    "setup.exe",
    "fxfight.cfg",
    "fight",
]


def Run_Command(Command: list[str]) -> None:
    print("Running:", " ".join(str(Item) for Item in Command))
    subprocess.run(Command, check=True)


def Find_Source_Item(SourceRoot: Path, ItemName: str) -> Path:
    for PathItem in SourceRoot.iterdir():
        if PathItem.name.lower() == ItemName.lower():
            return PathItem

    raise FileNotFoundError(f"Missing required source item: {ItemName}")


def Copy_Cd_Image(CuePath: Path, InstallRoot: Path) -> tuple[Path, Path]:
    """
    Copy the original CUE/BIN pair into the installation directory.

    Returns:
        (InstalledCuePath, InstalledBinPath)
    """

    CdDirectory = InstallRoot / "cd"
    CdDirectory.mkdir(parents=True, exist_ok=True)

    BinPath = Parse_Cue_Bin_Path(CuePath)

    InstalledCuePath = CdDirectory / CuePath.name
    InstalledBinPath = CdDirectory / BinPath.name

    print(f"Copying CD image: {CuePath} -> {InstalledCuePath}")
    shutil.copy2(CuePath, InstalledCuePath)

    print(f"Copying CD image: {BinPath} -> {InstalledBinPath}")
    shutil.copy2(BinPath, InstalledBinPath)

    return InstalledCuePath, InstalledBinPath

def Copy_Item(SourcePath: Path, DestinationPath: Path, Overwrite: bool) -> None:
    if DestinationPath.exists():
        if not Overwrite:
            print(f"Skipping existing: {DestinationPath}")
            return

        if DestinationPath.is_dir():
            shutil.rmtree(DestinationPath)
        else:
            DestinationPath.unlink()

    print(f"Copying: {SourcePath} -> {DestinationPath}")

    if SourcePath.is_dir():
        shutil.copytree(SourcePath, DestinationPath)
    else:
        shutil.copy2(SourcePath, DestinationPath)


def Fix_Permissions(InstallDir: Path) -> None:
    for PathItem in InstallDir.rglob("*"):
        if PathItem.is_dir():
            PathItem.chmod(0o755)
        else:
            PathItem.chmod(0o644)

    InstallDir.chmod(0o755)

    for ExePath in InstallDir.glob("*.EXE"):
        ExePath.chmod(0o755)


def Parse_Cue_Bin_Path(CuePath: Path) -> Path:
    for Line in CuePath.read_text(errors="ignore").splitlines():
        Line = Line.strip()

        if Line.upper().startswith("FILE"):
            Parts = Line.split('"')

            if len(Parts) >= 2:
                BinName = Parts[1]
                BinPath = CuePath.parent / BinName

                if not BinPath.exists():
                    raise FileNotFoundError(f"BIN referenced by CUE not found: {BinPath}")

                return BinPath

    raise ValueError(f"Could not find BIN reference in CUE file: {CuePath}")


def Mount_Cue_To_Temp_Source(CuePath: Path, WorkDir: Path) -> Path:
    BinPath = Parse_Cue_Bin_Path(CuePath)

    IsoPrefix = WorkDir / "fxfighter"
    MountDir = WorkDir / "mount"
    MountDir.mkdir(parents=True, exist_ok=True)

    Run_Command([
        "bchunk",
        str(BinPath),
        str(CuePath),
        str(IsoPrefix),
    ])

    IsoPath = WorkDir / "fxfighter01.iso"

    if not IsoPath.exists():
        raise FileNotFoundError(f"Expected ISO was not created: {IsoPath}")

    Run_Command([
        "fuseiso",
        str(IsoPath),
        str(MountDir),
    ])

    return MountDir


def Unmount_Fuse(MountDir: Path) -> None:
    subprocess.run(
        ["fusermount", "-u", str(MountDir)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def Write_FxFight_Cfg(InstallDir: Path, GameDirName: str, ScriptRoot: Path) -> None:
    WriterPath = ScriptRoot / "write_fxfight_cfg.py"

    if not WriterPath.exists():
        raise FileNotFoundError(f"Missing config writer script: {WriterPath}")

    Run_Command([
        sys.executable,
        str(WriterPath),
        "--output",
        str(InstallDir / "FXFIGHT.CFG"),
        "--install-dir",
        f"C:\\{GameDirName}",
        "--cd-drive",
        "D:",
    ])


def Build_DosBox_Config(
    InstallRoot: Path,
    CuePath: Path,
    OutputPath: Path,
    GameDirName: str,
    Cycles: int,
    ScriptRoot: Path,
) -> None:
    BuilderPath = ScriptRoot / "build_dosbox_config.py"

    if not BuilderPath.exists():
        raise FileNotFoundError(f"Missing DOSBox config builder script: {BuilderPath}")

    Run_Command([
        sys.executable,
        str(BuilderPath),
        "--install-root",
        str(InstallRoot),
        "--cue",
        str(CuePath),
        "--cycles",
        str(Cycles),
        "--game-dir",
        GameDirName,
        "--output",
        str(OutputPath),
    ])


def Install_From_Source(
    SourceRoot: Path,
    InstallRoot: Path,
    GameDirName: str,
    Overwrite: bool,
    ScriptRoot: Path,
) -> Path:
    if not SourceRoot.is_dir():
        raise FileNotFoundError(f"Source directory not found: {SourceRoot}")

    InstallDir = InstallRoot / GameDirName
    InstallDir.mkdir(parents=True, exist_ok=True)

    for ItemName in REQUIRED_ITEMS:
        SourcePath = Find_Source_Item(SourceRoot, ItemName)
        DestinationPath = InstallDir / SourcePath.name.upper()
        Copy_Item(SourcePath, DestinationPath, Overwrite)

    Fix_Permissions(InstallDir)
    Write_FxFight_Cfg(InstallDir, GameDirName, ScriptRoot)
    Fix_Permissions(InstallDir)

    return InstallDir


def Verify_Install(InstallDir: Path) -> None:
    RequiredInstalledItems = [
        "DOS4GW.EXE",
        "FIGHT.EXE",
        "SETUP.EXE",
        "FXFIGHT.CFG",
        "FIGHT",
    ]

    print()
    print("Verifying installation...")

    for ItemName in RequiredInstalledItems:
        ItemPath = InstallDir / ItemName

        if not ItemPath.exists():
            raise FileNotFoundError(f"Missing installed item: {ItemPath}")

        print(f"OK: {ItemPath}")

    print("Verification complete.")


def Main() -> int:
    Parser = argparse.ArgumentParser(
        description="Install FX Fighter from mounted CD files or a CUE/BIN image."
    )

    SourceGroup = Parser.add_mutually_exclusive_group(required=True)

    SourceGroup.add_argument(
        "--source",
        help="Mounted FX Fighter CD path, for example /mnt/fxfighter",
    )

    SourceGroup.add_argument(
        "--cue",
        help="Path to FX Fighter .cue file",
    )

    Parser.add_argument(
        "--install-root",
        required=True,
        help="DOSBox C: root / Lutris GAMEDIR",
    )

    Parser.add_argument(
        "--game-dir",
        default="FXFIGHT",
        help="Game directory name under install root. Default: FXFIGHT",
    )

    Parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing installed files.",
    )

    Parser.add_argument(
        "--cycles",
        type=int,
        # default=32000,
        default=36000,
        help="DOSBox fixed CPU cycles. Default: 32000",
    )

    Parser.add_argument(
        "--dosbox-conf",
        default=None,
        help="Optional output path for dosbox.conf. Defaults to install root/dosbox.conf when --cue is used.",
    )

    Parser.add_argument(
        "--skip-dosbox-config",
        action="store_true",
        help="Do not generate dosbox.conf.",
    )

    # Kept for compatibility with your current YAML.
    Parser.add_argument(
        "--skip-control-patch",
        action="store_true",
        help="Currently unused. CONFIG.DEF is generated by the game on first run.",
    )

    Args = Parser.parse_args()

    InstallRoot = Path(Args.install_root).expanduser().resolve()
    ScriptRoot = Path(__file__).resolve().parent

    try:
        InstallRoot.mkdir(parents=True, exist_ok=True)

        if Args.source:
            SourceRoot = Path(Args.source).expanduser().resolve()

            InstallDir = Install_From_Source(
                SourceRoot=SourceRoot,
                InstallRoot=InstallRoot,
                GameDirName=Args.game_dir,
                Overwrite=Args.overwrite,
                ScriptRoot=ScriptRoot,
            )

        else:
            CuePath = Path(Args.cue).expanduser().resolve()

            if not CuePath.exists():
                raise FileNotFoundError(f"CUE file not found: {CuePath}")

            InstalledCuePath, InstalledBinPath = Copy_Cd_Image(
                CuePath,
                InstallRoot,
            )

            with tempfile.TemporaryDirectory(prefix="fxfighter_") as TempDirText:
                TempDir = Path(TempDirText)
                MountDir = Mount_Cue_To_Temp_Source(CuePath, TempDir)

                try:
                    InstallDir = Install_From_Source(
                        SourceRoot=MountDir,
                        InstallRoot=InstallRoot,
                        GameDirName=Args.game_dir,
                        Overwrite=Args.overwrite,
                        ScriptRoot=ScriptRoot,
                    )
                finally:
                    Unmount_Fuse(MountDir)

            if not Args.skip_dosbox_config:
                DosBoxConfPath = (
                    Path(Args.dosbox_conf).expanduser().resolve()
                    if Args.dosbox_conf
                    else InstallRoot / "dosbox.conf"
                )

                Build_DosBox_Config(
                    InstallRoot=InstallRoot,
                    CuePath=InstalledCuePath,
                    OutputPath=DosBoxConfPath,
                    GameDirName=Args.game_dir,
                    Cycles=Args.cycles,
                    ScriptRoot=ScriptRoot,
                )

        Verify_Install(InstallDir)

        print()
        print("FX Fighter install complete.")
        print(f"Installed to: {InstallDir}")

        if Args.cue and not Args.skip_dosbox_config:
            print(f"DOSBox config: {Args.dosbox_conf or InstallRoot / 'dosbox.conf'}")

    except Exception as Ex:
        print(f"ERROR: {Ex}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(Main())