# Cloudflare DNS Setup for Knowmler

This guide walks you through configuring Cloudflare DNS for knowmler.com to point to your VPS.

## Prerequisites

- Knowmler.com registered (✅ you have this)
- Cloudflare account
- VPS with public IP address

## Step 1: Add Domain to Cloudflare

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click **"Add a Site"**
3. Enter: `knowmler.com`
4. Click **"Add site"**
5. Select the **Free** plan
6. Click **"Continue"**

## Step 2: Update Nameservers at Domain Registrar

Cloudflare will show you 2 nameservers (something like):
```
adonis.ns.cloudflare.com
hera.ns.cloudflare.com
```

**Go to your domain registrar** (where you registered knowmler.com) and:
1. Find the DNS/Nameserver settings
2. Replace the existing nameservers with Cloudflare's nameservers
3. Save changes

**⏰ This can take 24-48 hours to propagate**, but usually happens within 1-2 hours.

## Step 3: Add DNS Records

Once Cloudflare detects your domain, go to **DNS** → **Records** and add:

### A Record (Required)
Points your domain to your VPS IP address.

| Type | Name | IPv4 Address | Proxy Status | TTL |
|------|------|--------------|--------------|-----|
| A | @ | `YOUR_VPS_IP` | ✅ Proxied | Auto |

**Example:**
```
Type: A
Name: @ (represents knowmler.com)
IPv4 address: 192.0.2.45 (your VPS IP)
Proxy status: Proxied (orange cloud)
TTL: Auto
```

### WWW Record (Optional but Recommended)
Redirects www.knowmler.com to knowmler.com

| Type | Name | IPv4 Address | Proxy Status | TTL |
|------|------|--------------|--------------|-----|
| A | www | `YOUR_VPS_IP` | ✅ Proxied | Auto |

## Step 4: Configure SSL/TLS Settings

1. Go to **SSL/TLS** tab
2. Set encryption mode to **"Full (strict)"**
3. Go to **SSL/TLS** → **Edge Certificates**
4. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: 1.2

## Step 5: Create API Token for Caddy DNS Challenge

Knowmler uses Caddy with Cloudflare DNS challenge for automatic SSL certificates.

1. Go to **My Profile** (top right) → **API Tokens**
2. Click **"Create Token"**
3. Click **"Use template"** next to **"Edit zone DNS"**
4. Configure:
   - **Token name**: `Knowmler DNS Challenge`
   - **Permissions**:
     - Zone → DNS → Edit
   - **Zone Resources**:
     - Include → Specific zone → knowmler.com
5. Click **"Continue to summary"**
6. Click **"Create Token"**
7. **Copy the token** (starts with something like `aBcDeFgHiJkLmNoPqRsTuVwXyZ`)

**⚠️ Save this token securely - you'll need it for the VPS setup!**

## Step 6: Verify DNS Propagation

After adding the A record, verify it's working:

```bash
# Check if DNS is propagating
dig knowmler.com +short

# Should return your VPS IP address
```

Or use online tools:
- https://dnschecker.org/#A/knowmler.com
- https://www.whatsmydns.net/#A/knowmler.com

## Summary

✅ Domain added to Cloudflare
✅ Nameservers updated at registrar
✅ A record pointing to VPS IP
✅ SSL/TLS set to Full (strict)
✅ API token created for Caddy

**Next Step:** [VPS Deployment Guide](./VPS_DEPLOYMENT.md)

## Troubleshooting

### DNS not propagating after 24 hours
- Double-check nameservers at registrar match Cloudflare exactly
- Make sure you saved the changes at the registrar
- Try flushing your local DNS cache: `sudo dscacheutil -flushcache` (macOS)

### "Too many redirects" error
- Change SSL/TLS mode from "Flexible" to "Full (strict)"
- Make sure Caddy is configured with TLS enabled

### API token not working
- Verify token has "Edit" permission for DNS
- Check token is scoped to knowmler.com zone specifically
- Regenerate token if needed
