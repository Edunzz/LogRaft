# Dummy Log Generator (Ubuntu, single host)

Minimal **vendor-agnostic** log generator. It writes **JSON** and **human-readable** lines to a local file.  
Use it to demo and later **compare/migrate** log ingestion and dashboards (e.g., **from New Relic to Dynatrace**).

> This README only documents the log generator. Vendor setup is **not** included here.

---

## Requirements
- Ubuntu 20.04+ with `sudo`
- Python 3 and `python3-venv`

---

## Install

### 1) Create folders and venv
```bash
sudo mkdir -p /opt/demo-logger /var/log/demoapp
sudo chown -R $USER:$USER /opt/demo-logger /var/log/demoapp

sudo apt update && sudo apt install -y python3 python3-venv
python3 -m venv /opt/demo-logger/venv
/opt/demo-logger/venv/bin/pip install --upgrade pip loguru
```

### 2) Copy the app
Save **logger.py** to `/opt/demo-logger/logger.py` and make it executable:
```bash
sudo cp -f logger.py /opt/demo-logger/logger.py
sudo chmod 755 /opt /opt/demo-logger /opt/demo-logger/logger.py
sudo chmod -R 755 /opt/demo-logger/venv/bin
# if pasted from Windows:
sudo sed -i 's/\r$//' /opt/demo-logger/logger.py
```

### 3) (Recommended) Install as a systemd service
Save **demo-logger.service** to `/etc/systemd/system/demo-logger.service` and enable it:
```bash
sudo cp -f demo-logger.service /etc/systemd/system/demo-logger.service
sudo systemctl daemon-reload
sudo systemctl enable --now demo-logger
sudo systemctl status demo-logger --no-pager
```

---

## Live view

```bash
tail -f /var/log/demoapp/app.log
# or
journalctl -u demo-logger -f --no-pager
```

Examples while watching:
```bash
tail -f /var/log/demoapp/app.log | grep ERROR
journalctl -u demo-logger -f | grep '"endpoint":"\/pay"'
```

---

## What’s next?

Use this generator as the **source of truth** for synthetic logs when you demonstrate **log ingestion, parsing, dashboards, and migration** (e.g., from **New Relic to Dynatrace**).

---

## Troubleshooting
- **code=203/EXEC / Permission denied** → ensure the service uses the venv interpreter in `ExecStart`, and that folders are `chmod 755`.
- **/opt mounted with noexec** → move to `/usr/local/demo-logger` and update paths in the service file.
- **No logs** → check dir permissions and recent service output:
  ```bash
  journalctl -u demo-logger -b -n 100 --no-pager
  ```

---

## Cleanup
```bash
sudo systemctl disable --now demo-logger
sudo rm -f /etc/systemd/system/demo-logger.service
sudo systemctl daemon-reload
sudo rm -rf /opt/demo-logger /usr/local/demo-logger /var/log/demoapp
```
