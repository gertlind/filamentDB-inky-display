
# Service file for Reader Pi
- Change : User, WorkingDirectory, ExecStart to fit your installation.
- Change : Environment USER:PASSWORD to your MongoDB user. 
```bash
sudo nano /etc/systemd/system/filament_to_inky.service
```
```ini
[Unit]
Description=Filament NFC to Inky
After=network-online.target pcscd.service
Wants=network-online.target pcscd.service
[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=%h/filamentDB-inky-display/reader
Environment="MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster.mongodb.net/filament-db?retryWrites=true&w=majority"
ExecStart=%h/filamentDB-inky-display/.venv/bin/python \
%h/filamentDB-inky-display/reader/filament_to_inky.py \
--inky http://INKY_PI_IP:5000/filament
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable filament_to_inky.service
sudo systemctl start filament_to_inky.service
```
View logs:
```bash
journalctl -u filament_to_inky.service -f
```