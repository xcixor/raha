# Raha Deployment Plan: Local Server

## Objective
Host the **Raha** application on a local laptop server using production-grade containerization. This setup ensures data persistence, local network accessibility, and easy migration to public internet access later.

## 🏗 Architecture

The application runs as a multi-container Docker application:

1.  **Nginx (Reverse Proxy)**: 
    - Entry point for all requests.
    - Serves static files (`/static/`) and media uploads (`/media/`) directly from disk for high performance.
    - Proxies application traffic to the Django container.
    - Listens on Port 80.

2.  **Web (Django + Gunicorn)**:
    - Runs the Python/Django application code.
    - Uses `gunicorn` as the WSGI server.
    - Stateless container (code only).

3.  **Database (PostgreSQL)**:
    - Persistent relational database.
    - Data stored on the laptop's filesystem via bind mounts.

## 📂 Data Persistence (Bind Mounts)

Data is stored directly on the host laptop's filesystem, mapped into containers. This allows for easy backups and file browsing on the host machine.

| Host Path (Laptop) | Container Path | Description |
| :--- | :--- | :--- |
| `./media_data/` | `/app/media/` | User-uploaded images & videos. |
| `./static_data/` | `/app/static/` | CSS, JS, and asset files. |
| `./db_data/` | `/var/lib/postgresql/data` | PostgreSQL database files. |

## 🛠 Prerequisites (Laptop Setup)

1.  **Operating System**: Linux (Ubuntu Server 24.04 recommended) or existing OS with Docker Desktop.
2.  **Docker**: Install Docker Engine and Docker Compose.
3.  **Power Settings**: Ensure the laptop **does not sleep** when the lid is closed.
    - *Linux*: Edit `/etc/systemd/logind.conf` -> `HandleLidSwitch=ignore` -> `sudo systemctl restart systemd-logind`.
4.  **Network**: Assign a **Static IP** to the laptop on your router (e.g., `192.168.1.50`) for consistent local access.

## 🚀 Deployment Steps

### 1. Clone & Prepare
```bash
git clone https://github.com/xcixor/raha.git
cd raha

# Create data directories
mkdir -p media_data static_data db_data
```

### 2. Configuration
Create a `.env` file in the root directory:
```bash
DEBUG=False
SECRET_KEY=your_production_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.50  # Add your laptop's LAN IP
DATABASE=postgres
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=raha
SQL_USER=raha_user
SQL_PASSWORD=raha_pass
SQL_HOST=db
SQL_PORT=5432
```

### 3. Build & Run
```bash
# Build and start containers in detached mode
docker-compose -f docker-compose.prod.yml up -d --build
```

### 4. Verify
- **Browser**: Visit `http://localhost` (on laptop) or `http://192.168.1.50` (on phone/LAN).
- **Logs**: `docker-compose -f docker-compose.prod.yml logs -f`

## 🔄 Maintenance & Updates

### Updating the App
When you push code changes to GitHub:
```bash
git pull origin feat/verification-system
docker-compose -f docker-compose.prod.yml up -d --build web
```

### Backups
To backup your entire server state, simply copy the data folders:
```bash
# Stop containers to ensure data integrity
docker-compose -f docker-compose.prod.yml down

# Backup folders
tar -czvf raha_backup_$(date +%F).tar.gz media_data/ db_data/ .env

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

## 🔮 The Cloudflare Tunnel (Anonymous Mode)

To expose the app securely to the internet without revealing your home IP:

### 1. Generate a Tunnel Token
1.  **Log in to Cloudflare Dashboard** -> **Zero Trust** -> **Access** -> **Tunnels**.
2.  Click **Create a Tunnel**. Name it (e.g., `raha-home`).
3.  Choose **Docker** as your environment.
4.  Copy the token from the provided command (look for `token: eyJh...`).

### 2. Configure the Tunnel
Add the token to your `.env` file:
```bash
TUNNEL_TOKEN=eyJhIjoi...
```

### 3. Configure the Public Hostname
In the Cloudflare Dashboard (Tunnel settings):
1.  Add a **Public Hostname** (e.g., `raha.yourdomain.com`).
2.  Set **Service** to `http://nginx:80`. (This points the tunnel to your local Nginx container).

### 4. Restart
```bash
docker-compose -f docker-compose.prod.yml up -d
```
Your app is now live at `https://raha.yourdomain.com` with full SSL encryption and your IP hidden.
