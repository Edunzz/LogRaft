# Laboratorio de Logs en un solo Ubuntu (New Relic vs Dynatrace)

Guía paso a paso (sin contenedores, sin Fluent). Genera logs locales, los reenvías a **New Relic** y **Dynatrace**, y creas consultas para un dashboard simple en cada plataforma.

---

## 0) Requisitos

- Ubuntu 20.04+ con sudo.
- Acceso a internet.
- **Licencia** de New Relic (`<NR_LICENSE>`) y acceso a tu **tenant** Dynatrace.
- Usuario con permisos para crear servicios `systemd`.

---

## 1) Estructura de carpetas

```bash
sudo mkdir -p /opt/demo-logger /var/log/demoapp
sudo chown -R $USER:$USER /opt/demo-logger /var/log/demoapp
```

---

## 2) Entorno Python y dependencias

```bash
sudo apt update && sudo apt install -y python3 python3-venv
python3 -m venv /opt/demo-logger/venv
/opt/demo-logger/venv/bin/pip install --upgrade pip loguru
```

---

## 3) Script generador de logs

**Archivo:** `/opt/demo-logger/logger.py`
```python
#!/opt/demo-logger/venv/bin/python
from loguru import logger
import time, json, random, string, os

os.makedirs("/var/log/demoapp", exist_ok=True)

logger.add("/var/log/demoapp/app.log",
           rotation="10 MB",
           retention="3 days",
           compression="gz",
           enqueue=True,
           format="{time:YYYY-MM-DDTHH:mm:ss.SSS} | {level:<7} | {message}")

levels    = ["DEBUG","INFO","WARNING","ERROR"]
endpoints = ["/login","/pay","/search","/orders","/items"]
users     = ["alice","bob","carol","dan","erin"]

def rid(n=8): 
    import string, random
    return "".join(random.choices(string.ascii_letters+string.digits, k=n))

while True:
    evt = {
        "event": "request",
        "id": rid(),
        "user": random.choice(users),
        "endpoint": random.choice(endpoints),
        "latency_ms": random.randint(5, 1200),
        "ok": random.choice([True, True, True, False])
    }
    lvl = random.choice(levels)
    # Línea JSON (para parsear fácil en NR/Dynatrace)
    logger.log(lvl, json.dumps(evt))
    # Línea legible
    logger.log(lvl, f"{evt['user']} -> {evt['endpoint']} in {evt['latency_ms']}ms ok={evt['ok']}")
    time.sleep(random.uniform(0.2, 1.5))
```

**Permisos:**
```bash
sudo chmod 755 /opt /opt/demo-logger /opt/demo-logger/logger.py
sudo chmod -R 755 /opt/demo-logger/venv/bin
# (opcional) si copiaste desde Windows
sudo sed -i 's/\r$//' /opt/demo-logger/logger.py
```

> Si tu `/opt` estuviera montado con **noexec**, muévete a `/usr/local/demo-logger` y ajusta rutas del servicio (ver sección 5).

---

## 4) Servicio systemd

**Archivo:** `/etc/systemd/system/demo-logger.service`
```ini
[Unit]
Description=Demo Log Generator
After=network.target

[Service]
Type=simple
ExecStart=/opt/demo-logger/venv/bin/python /opt/demo-logger/logger.py
WorkingDirectory=/opt/demo-logger
User=root
Restart=always
RestartSec=1
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

**Activación:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now demo-logger
sudo systemctl status demo-logger --no-pager
```

**Ver en vivo:**
```bash
tail -f /var/log/demoapp/app.log
# o
journalctl -u demo-logger -f --no-pager
```

---

## 5) Notas de permisos y “permission denied”

- Asegura `chmod 755` en directorios e intérprete.
- Invoca **siempre** el intérprete del venv en `ExecStart` (más robusto que usar el shebang).
- Si `/opt` está con `noexec`:
  ```bash
  sudo mkdir -p /usr/local/demo-logger
  sudo rsync -a /opt/demo-logger/ /usr/local/demo-logger/
  sudo sed -i 's#/opt/demo-logger#/usr/local/demo-logger#g' /etc/systemd/system/demo-logger.service
  sudo systemctl daemon-reload && sudo systemctl restart demo-logger
  ```
