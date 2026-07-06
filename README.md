# Blade Runner Lutris Installer Fix

## Bug

The current Lutris Blade Runner GOG installer can receive the native Linux GOG installer:

blade_runner_1_0_svm_src_34722.sh

but attempts to extract it using `format: gog`, which expects a Windows/Inno GOG setup executable. This causes:

specified exe is not a GOG setup file


## Proposed Fix

- Extract the Linux installer using `format: zip`.
- Merge the extracted `data/noarch` directory into the game directory.
- Configure the game to use the ScummVM runner.
- Set the game path to `$GAMEDIR/game/data`.


## Test Environment

- Operating System: Ubuntu 24.04.4 LTS (64-bit)
- Lutris: 0.5.22
- Installation Source: GOG offline Linux installer
- Runner: ScummVM (Lutris)

## Reproduction

1. Install Blade Runner from GOG through Lutris on Linux.
2. Lutris downloads the Linux `.sh` installer.
3. The installer attempts `format: gog`.
4. Installation fails with `specified exe is not a GOG setup file`.

## Verification

Using the updated installer:

1. Select `blade_runner_1_0_svm_src_34722.sh`.
2. The installer extracts successfully with `format: zip`.
3. Lutris registers the game with the ScummVM runner.
4. Blade Runner launches successfully from `$GAMEDIR/game/data`.

## Status

This installer has been validated locally and is awaiting community review before submission upstream
