# FilamentDB → Inky Display
<p align="center">
<img src="images/inky_pic.png" width="700">
</p>

## Features
- Display filament information from [Filament-DB](https://github.com/hyiger/filament-db/blob/main/README.md)
- Read [OpenPrintTag](https://openprinttag.org) NFC tags using ACS ACR1552U reader/writer
- Lookup filament data directly from MongoDB
- Does not need an installation of Filament DB software
- Send filament data to a remote Inky display
- Material icons for PLA / PETG / TPU etc.
- Designed for Raspberry Pi + systemd services

## Filament-DB
Filament-DB is a software that let you keep track on all your filaments.
This project relies on the database that Filament-DB uses.
You need to set up your instance of Filament-DB in order to use these scripts. You don't need to run FilamentDB on the Reader Pi, it reads the FilamentDB mongo database directly from MongoDB Atlas.
[Read all about how to set up and use FilamentDB.](https://github.com/hyiger/filament-db/blob/main/README.md)

## Hardware
Hardware needed for this project:

### Reader Pi
* Raspberry Pi5
* [ACS ACR1552U NFC reader](https://www.amazon.com/dp/B0CJPXCYWK?ref=ppx_yo2ov_dt_b_fed_asin_title)

### Display Pi
* Raspberry Pi Zero 2W
* Pimoroni Inky Impression 7.3”

### NFC Tags
* [iCode SLIX2 Sticker Label,ISO/IEC 15693 HF Dia 25mm](https://www.amazon.com/iCode-SLIX2-Sticker-Library-Labels/dp/B07GBMJNWL/ref=sr_1_1?crid=14NT4Y8JSX9XP&dib=eyJ2IjoiMSJ9.LHduxonTvezmhWVocwBilNgLU67k89YBYv1EsK89WEQOf1M02EF8DFdBVrYux3ANp0nF0NoeOAG188ACbnoLlA.RaFTAM63giFurPgFDITM1sKnTnKFzB2uM3zUw6nP8O4&dib_tag=se&keywords=NXP%2BICode%2BSLIX2%2BSticker%2BLabel%2C%2BISO%2FIEC%2B15693%2BHF%2BDia%2B25mm%2C%2BRFID%2BLibrary%2BLabels%2B(20)&nsdOptOutParam=true&qid=1778483565&sprefix=nxp%2Bicode%2Bslix2%2Bsticker%2Blabel%2C%2Biso%2Fiec%2B15693%2Bhf%2Bdia%2B25mm%2C%2Brfid%2Blibrary%2Blabels%2B20%2B%2Caps%2C328&sr=8-1&th=1)

### Installation
- [Installation Guide](docs/install.md)