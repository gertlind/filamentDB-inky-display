# Installation
## Reader Pi
- sudo apt update
- sudo apt full-upgrade -y
- sudo reboot
```bash
sudo apt install -y\
    git \
    pcscd \
    pcsc-tools \
    libpcsclite-dev \
    build-essential \
    python3-dev \
    python3-venv
```
- git clone https://github.com/gertlind/filamentDB-inky-display.git
- cd filamentDB-inky-display
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r reader/requirements.txt
- deactivate

## Inky Pi
### Updates
- sudo apt update
- sudo apt full-upgrade -y
- sudo reboot
```bash
sudo apt install -y \
    git \
    python3-dev \
    python3-venv \
    libopenjp2-7 \
    libtiff6 \
    libatlas-base-dev
```
### Activate SPI
- sudo raspi-config → Interface Options → SPI → Enable
## Configure and enable services.
- [Reader service](/docs/readerservice.md)
- [Inky Pi service](/docs/inkyservice.md)
