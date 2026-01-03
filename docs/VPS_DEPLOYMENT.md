# VPS Deployment Guide for Knowmler

This guide covers deploying Knowmler to a VPS (Virtual Private Server) with Docker.

## Prerequisites

- ✅ VPS with Ubuntu 22.04+ (recommended) or similar Linux distribution
- ✅ Root or sudo access
- ✅ Domain configured in Cloudflare (see [Cloudflare DNS Setup](./CLOUDFLARE_DNS_SETUP.md))
- ✅ Cloudflare API token for DNS challenge
- ✅ OpenAI API key
- Minimum specs:
  - **CPU**: 2 cores
  - **RAM**: 4GB
  - **Storage**: 20GB

## Step 1: Connect to Your VPS

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Or if using a non-root user:
ssh username@YOUR_VPS_IP
```

## Step 2: Update System & Install Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    git \
    curl \
    ca-certificates \
    gnupg \
    lsb-release
```

## Step 3: Install Docker & Docker Compose

```bash
# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version

# Add your user to docker group (optional, avoids needing sudo)
sudo usermod -aG docker $USER
```

**⚠️ Log out and back in** for the docker group change to take effect.

## Step 4: Clone Knowmler Repository

```bash
# Create directory for the app
mkdir -p /opt/knowmler
cd /opt/knowmler

# Clone repository
git clone https://github.com/snedea/yt-transcript-downloader.git .

# Or if you have a private fork:
# git clone https://github.com/YOUR_USERNAME/yt-transcript-downloader.git .
```

## Step 5: Configure Environment Variables

```bash
# Create .env file from example
cp .env.example .env

# Edit the .env file
nano .env
```

**Add/update the following:**

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Cloudflare API Token (for DNS challenge)
CF_API_TOKEN=your-cloudflare-api-token-here

# Environment
ENVIRONMENT=production

# CORS Origins (update with your domain)
CORS_ORIGINS=["https://knowmler.com", "https://www.knowmler.com"]

# Database
DATABASE_URL=sqlite:///./data/knowmler.db

# Security (generate a secure random string)
SECRET_KEY=$(openssl rand -hex 32)
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

## Step 6: Configure Caddyfile

The Caddyfile should already be configured for knowmler.com from the rebranding. Verify it:

```bash
cat Caddyfile
```

Should show:
```
knowmler.com {
    tls {
        dns cloudflare {env.CF_API_TOKEN}
    }
    ...
}
```

## Step 7: Create Data Directories

```bash
# Create directories for persistent data
mkdir -p data uploads/pdfs uploads/thumbnails

# Set permissions
chmod -R 755 data uploads
```

## Step 8: Deploy with Docker Compose

```bash
# Build and start containers
docker compose up -d --build

# Check container status
docker compose ps

# View logs
docker compose logs -f

# To stop following logs, press Ctrl+C
```

**Expected output:**
```
NAME                                  STATUS
yt-transcript-downloader-backend-1    Up (healthy)
yt-transcript-downloader-frontend-1   Up
yt-transcript-downloader-caddy-1      Up
```

## Step 9: Verify Deployment

### Check containers are running:
```bash
docker compose ps
```

### Check backend health:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### Check frontend:
```bash
curl http://localhost:3000
```

Should return HTML content.

### Access via domain:
Visit https://knowmler.com in your browser.

## Step 10: Set Up Automatic Backups (Recommended)

```bash
# Create backup script
cat > /opt/knowmler/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/knowmler/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp data/knowmler.db $BACKUP_DIR/knowmler_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# Make executable
chmod +x /opt/knowmler/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/knowmler/backup.sh >> /var/log/knowmler-backup.log 2>&1") | crontab -
```

## Step 11: Set Up Auto-Update (Optional)

```bash
# Create update script
cat > /opt/knowmler/update.sh << 'EOF'
#!/bin/bash
cd /opt/knowmler

# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker compose up -d --build

echo "Update completed: $(date)"
EOF

# Make executable
chmod +x /opt/knowmler/update.sh
```

Run manually when you want to update:
```bash
/opt/knowmler/update.sh
```

## Useful Commands

### View logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f caddy
```

### Restart services:
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Stop services:
```bash
docker compose down
```

### Update and restart:
```bash
cd /opt/knowmler
git pull origin main
docker compose up -d --build
```

### Check disk usage:
```bash
du -sh /opt/knowmler/*
docker system df
```

### Clean up Docker resources:
```bash
# Remove unused images
docker image prune -a

# Remove all unused resources
docker system prune -a --volumes
```

## Firewall Configuration (Optional but Recommended)

```bash
# Install UFW (Uncomplicated Firewall)
sudo apt install -y ufw

# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Troubleshooting

### Containers won't start
```bash
# Check logs for errors
docker compose logs

# Verify .env file is configured
cat .env | grep -v '^#' | grep -v '^$'

# Rebuild from scratch
docker compose down -v
docker compose up -d --build
```

### Can't access via domain
```bash
# Verify DNS is pointing to VPS IP
dig knowmler.com +short

# Check Caddy logs
docker compose logs caddy

# Verify Cloudflare API token is correct
cat .env | grep CF_API_TOKEN
```

### SSL certificate issues
```bash
# Check Caddy logs for DNS challenge errors
docker compose logs caddy | grep -i error

# Verify Cloudflare API token has DNS edit permissions
# Regenerate token if needed
```

### Out of disk space
```bash
# Check disk usage
df -h

# Clean Docker resources
docker system prune -a --volumes

# Check application data
du -sh /opt/knowmler/*
```

### Database locked errors
```bash
# Check if multiple processes are accessing DB
lsof /opt/knowmler/data/knowmler.db

# Restart backend
docker compose restart backend
```

## Security Recommendations

1. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Use SSH keys instead of passwords**

3. **Change default SSH port** (edit /etc/ssh/sshd_config)

4. **Install fail2ban:**
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   ```

5. **Regular backups** (see Step 10 above)

6. **Monitor logs regularly:**
   ```bash
   docker compose logs -f | grep -i error
   ```

## Next Steps

✅ Knowmler is now running at https://knowmler.com
- Create your first user account
- Upload some content (YouTube videos, PDFs)
- Test the analysis features
- Set up monitoring (optional)

---

Need help? Check the [main README](../README.md) or open an issue on GitHub.
