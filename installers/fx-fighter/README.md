# FX Fighter Lutris Installer

A Lutris/DOSBox installer for the retail DOS CD-ROM version of **FX Fighter**.

This project installs and configures FX Fighter from the user's original `.cue/.bin`
CD image. It does not include or distribute the game.

## Status

Working:

- Installs from retail `.cue/.bin`
- Copies required game files
- Generates `FXFIGHT.CFG`
- Generates `dosbox.conf`
- Copies the CD image into the install directory
- Launches through Lutris
- Uses DOSBox with `cycles=fixed 36000`

## Requirements

- Linux
- Lutris
- DOSBox
- Python 3
- `bchunk`
- `fuseiso`
- Original FX Fighter `.cue/.bin` CD image

## Install dependencies on Ubuntu:
sudo apt install dosbox bchunk fuseiso

## Install

lutris -i installer/fx-fighter.yml

# Installed Layout

fx-fighter/
├── dosbox.conf
├── cd/
│   ├── fx_fighter.cue
│   └── fx_fighter.bin
└── FXFIGHT/
    ├── DOS4GW.EXE
    ├── FIGHT.EXE
    ├── FXFIGHT.CFG
    └── FIGHT/

## Notes

FX Fighter performs a CD-ROM check, so the original image is preserved and mounted by DOSBox at runtime.

## Legal

This repository contains installer scripts only.

It does not include FX Fighter, game data, executable files, CD images, artwork,
trademarks, or other copyrighted game content. Users must provide their own
legally obtained copy of the game.


