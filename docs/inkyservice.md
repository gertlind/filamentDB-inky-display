# Service file for Inky Pi
- Change : User, WorkingDirectory, ExecStart to fit your installation.
```bash
sudo nano /etc/systemd/system/inky_receiver.service
```

```ini
[Unit]
Description=Inky JSON Receiver
After=network-online.target
[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=%h/python/filamentDB-inky-display/inky
ExecStart=%h/python/filamentDB-inky-display/.venv/bin/python \
%h/python/filamentDB-inky-display/inky/inky_receiver.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable inky_receiver.service
sudo systemctl start inky_receiver.service
```
View logs:

```bash
journalctl -u inky_receiver.service -f
```