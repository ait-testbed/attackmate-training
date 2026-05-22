# AttackMate Training — Environment Setup Guide

This guide covers everything needed to run all examples, walkthroughs, and exercises across all four training days. All commands assume an Ubuntu/Debian-based attacker machine.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Core Tools](#2-core-tools)
3. [AttackMate](#3-attackmate)
4. [Metasploit Framework](#4-metasploit-framework)
5. [Sliver C2](#5-sliver-c2-day-2--instructor-demo-only)
6. [Bettercap](#6-bettercap-day-4)
7. [Browser Automation (Playwright)](#7-browser-automation-playwright-day-4)
8. [Wordlists](#8-wordlists)
9. [SSH Configuration for Metasploitable2](#9-ssh-configuration-for-metasploitable2)
10. [Firewall / Port Configuration](#10-firewall--port-configuration)
11. [AttackMate Config File Reference](#11-attackmate-config-file-reference)
12. [Target: Metasploitable2](#12-target-metasploitable2)
13. [Quick Verification Checklist](#13-quick-verification-checklist)

---

## 1. System Overview

```
Attacker machine  ←→  Metasploitable2 target (Ubuntu 8.04)
172.17.0.127           172.17.0.106
(your machine)         (VM / container)
```

Replace `172.17.0.127` (attacker) and `172.17.0.106` (target) with your actual IPs wherever you see `CHANGE_ME_ATTACKER` / `CHANGE_ME` in the playbooks.

---

## 2. Core Tools

Install all standard networking and pentesting utilities:

```bash
sudo apt update && sudo apt install -y \
  nmap \
  hydra \
  netcat-openbsd \
  curl \
  wget \
  openssh-client \
  openssh-server \
  python3 \
  python3-pip \
  iptables \
  ufw \
  net-tools \
  iproute2
```


### Tool reference

| Tool | Used for | Days |
|------|----------|------|
| `nmap` | Port scanning, service detection | 1–4 |
| `hydra` | Credential brute-forcing (FTP, SSH) | 1–4 |
| `netcat` (`nc`) | Port checks, reverse shells, listeners | 1–4 |
| `curl` | HTTP requests | 3–4 |
| `wget` | File download on target | 2–4 |
| `ssh` / `scp` | Remote access, file transfer | 1–4 |
| `python3` | Shell upgrades (`pty.spawn`), HTTP server | 1–4 |

---

## 3. AttackMate

AttackMate is the main tool for this training. It requires Python and `uv`.

### Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc   # or restart your shell
```

### Install AttackMate

```bash
# From the AttackMate project directory (not this training repo):
uv sync --dev
```

### Verify

```bash
attackmate --version
```

### Basic usage

```bash
# Run a playbook
attackmate playbook.yml

# With debug output
attackmate --debug playbook.yml

# With a config file (required for Day 2, 3, 4)
attackmate --config config.yml playbook.yml
```

---

## 4. Metasploit Framework

Required for Day 2, 3, and 4. AttackMate communicates with Metasploit via its RPC daemon.

### Install

```bash
# Recommended: use the official installer
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall
```

Or via apt (older version):

```bash
sudo apt install -y metasploit-framework
```

### Start the RPC daemon

The RPC daemon must be running before any `msf-*` command in AttackMate works:

```bash
msfrpcd -P msf -a 127.0.0.1
```

Verify it is listening on port 55553:

```bash
ss -tlnp | grep 55553
```

### Config file entry (required)

Create a `config.yml` with at minimum:

```yaml
msf_config:
  password: msf
  ssl: true
  port: 55553
  server: 127.0.0.1
```

Then run AttackMate with:

```bash
attackmate --config config.yml playbook.yml
```

### Ports used by Metasploit

| Port | Purpose |
|------|---------|
| 55553 | Metasploit |
| 4444 | Default multi/handler listener |
| 4422 | Alternate listener (Samba exploits) |
| 4433 | Alternate listener (Meterpreter upgrade) |
| 4344 | Alternate listener (PHP-CGI exploits) |

---

## 5. Sliver C2 (Day 2 — instructor demo only)

Sliver is covered in the Day 2 handout as a conceptual module, but there are **no participant exercises or runnable playbooks** for it. It is an instructor-led demo only. Participants do not need Sliver installed.

If you are the instructor and want to run the Sliver demo:

```bash
# Install
curl https://sliver.sh/install | sudo bash

# Start server
sudo sliver-server

# Generate operator config (inside Sliver console)
new-operator --name trainee --lhost <ATTACKER_IP>
# → writes to ~/.sliver-client/configs/operator.cfg

# Connect client
sliver-client --config ~/.sliver-client/configs/operator.cfg
```

Add to `config.yml`:

```yaml
sliver_config:
  config_file: /home/user/.sliver-client/configs/operator.cfg
```

Ports: **31337** (operator gRPC), **443/80** (implant listeners).

---

## 6. Bettercap (Day 4)

Bettercap is used for network-layer attacks (ARP spoofing, MITM) in Day 4.

### Install

```bash
sudo apt install -y bettercap
```

Or build from source:

```bash
sudo apt install -y golang
go install github.com/bettercap/bettercap@latest
```

### Start with REST API enabled

```bash
sudo bettercap -eval "set api.rest.username btrcp; set api.rest.password secret; api.rest on"
```

The REST API listens on port **8081** by default.

### Config file entry

```yaml
bettercap_config:
  - url: http://127.0.0.1:8081
    username: btrcp
    password: secret
```

---

## 7. Browser Automation / Playwright (Day 4)

### Install dependencies

```bash
# From the AttackMate project directory:
uv sync --dev
uv run playwright install chromium

# System dependencies for Chromium:
sudo apt install -y \
  libglib2.0-0 \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libdbus-1-3 \
  libxkbcommon0 \
  libx11-6 \
  libxcomposite1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libpango-1.0-0 \
  libasound2
```

Or use the Playwright helper:

```bash
uv run playwright install-deps chromium
```

---

## 8. Wordlists

### Install SecLists

```bash
sudo apt install -y seclists
```

The wordlists are installed to `/usr/share/SecLists/`.

Wordlist used in exercises:

```
/usr/share/SecLists/Passwords/darkweb2017_top-1000.txt
```

---

## 9. SSH Configuration for Metasploitable2

Metasploitable2 runs **Ubuntu 8.04** with a very old OpenSSH version that uses deprecated key exchange algorithms. Modern SSH clients refuse to connect by default.

### Add legacy algorithm support

Edit (or create) `~/.ssh/config`:

```bash
nano ~/.ssh/config
```

Add the following block (replace the IP with your actual Metasploitable2 IP):

```
Host CHANGE_ME
    HostKeyAlgorithms +ssh-rsa,ssh-dss
    PubkeyAcceptedKeyTypes +ssh-rsa,ssh-dss

```


Set correct permissions:

```bash
chmod 600 ~/.ssh/config
```

### Default SSH credentials on Metasploitable2

| Username | Password |
|----------|----------|
| `msfadmin` | `msfadmin` |
| `user` | `user` |
| `root` | (disabled direct login) |

### SSH key setup (for playbooks using key auth)

Metasploitable2's OpenSSH is too old to support modern key types. Only the following work:

| Key type | Supported | Command |
|----------|-----------|---------|
| RSA (2048-bit) | Yes | `ssh-keygen -t rsa -b 2048 -f ~/.ssh/metasploitable_key -N ""` |
| DSA (1024-bit) | Yes | `ssh-keygen -t dsa -f ~/.ssh/metasploitable_key -N ""` |
| ECDSA | No | Not supported by this OpenSSH version |
| Ed25519 | No | Requires OpenSSH 6.5+; Ubuntu 8.04 is far older |

Use RSA:

```bash
ssh-keygen -t rsa -b 2048 -f ~/.ssh/metasploitable_key -N ""
```

> Modern OpenSSH defaults to Ed25519. If you run `ssh-keygen` without `-t rsa` the generated key will not work on Metasploitable2.

---

## 10. Firewall / Port Configuration

The attacker machine needs to **accept inbound connections** on callback/listener ports so that reverse shells and Meterpreter sessions can connect back.

### Allow common listener ports

```bash
sudo ufw allow 4444/tcp    # Default MSF handler
sudo ufw allow 4422/tcp    # Alternate handler
sudo ufw allow 4433/tcp    # Meterpreter upgrade
sudo ufw allow 4344/tcp    # PHP-CGI handler
sudo ufw allow 8080/tcp    # webserv file server
sudo ufw allow 8081/tcp    # Bettercap REST API
sudo ufw allow 55553/tcp   # Metasploit RPC (if accessing from other host)
sudo ufw allow 31337/tcp   # Sliver operator gRPC
sudo ufw allow 443/tcp     # Sliver HTTPS listener
```

Or use iptables directly:

```bash
sudo iptables -A INPUT -p tcp --dport 4444 -j ACCEPT
# (repeat for each port above)
```

Verify rules:

```bash
sudo iptables -L INPUT -n -v --line-numbers
```

### port reference

| Port | Direction | Service |
|------|-----------|---------|
| 22 | → target | SSH to Metasploitable2 |
| 21 | → target | FTP on Metasploitable2 |
| 80 | → target | HTTP on Metasploitable2 |
| 139/445 | → target | Samba on Metasploitable2 |
| 3632 | → target | distcc on Metasploitable2 |
| 6667 | → target | UnrealIRCd on Metasploitable2 |
| 6200 | → target | vsftpd backdoor shell |
| 4444 | ← attacker | Default MSF reverse handler |
| 4422 | ← attacker | Samba exploit handler |
| 4433 | ← attacker | Meterpreter upgrade |
| 4344 | ← attacker | PHP-CGI handler |
| 8080 | ← attacker | webserv HTTP delivery |
| 8081 | ← attacker | Bettercap REST API |
| 55553 | localhost | Metasploit RPC daemon |
| 31337 | localhost | Sliver gRPC |
| 443 | ← attacker | Sliver HTTPS listener |

---

## 11. AttackMate Config File Reference

A full `config.yml` for Day 4 (all integrations):

```yaml
msf_config:
  password: msf
  ssl: true
  port: 55553
  server: 127.0.0.1

sliver_config:
  config: /root/.sliver-client/configs/operator.cfg

bettercap_config:
  - url: http://127.0.0.1:8081
    username: btrcp
    password: secret

cmd_config:
  loop_sleep: 5
  command_delay: 0
```

For Day 2/3, only `msf_config` is required.
For Sliver exercises, add `sliver_config`.
For Bettercap exercises, add `bettercap_config`.

---

## 12. Target: Metasploitable2

Metasploitable2 is a deliberately vulnerable Ubuntu 8.04 VM.

### Download

- Official: https://sourceforge.net/projects/metasploitable/
- Or use the Docker image: `tleemcjr/metasploitable2`

### Docker quick start

```bash
docker pull tleemcjr/metasploitable2
docker run -d --name metasploitable2 tleemcjr/metasploitable2
docker inspect metasploitable2 | grep IPAddress
```

### Key vulnerable services on Metasploitable2

| Port | Service | Vulnerability |
|------|---------|---------------|
| 21 | vsftpd 2.3.4 | Backdoor (CVE-2011-2523) — connects back on port 6200 |
| 22 | OpenSSH | Weak credentials |
| 80 | Apache + PHP-CGI | CVE-2012-1823 (argument injection) |
| 139/445 | Samba 3.0.20 | CVE-2007-2447 (username map script) |
| 3632 | distcc | CVE-2004-2687 (remote code execution) |
| 6667 | UnrealIRCd 3.2.8.1 | Backdoor |

---

## 13. Quick Verification Checklist

Run through this before starting each day:

### Day 1
- [ ] `nmap --version`
- [ ] `hydra --version`
- [ ] `nc -h` (netcat)
- [ ] `attackmate --version`
- [ ] SSH to Metasploitable2: `ssh msfadmin@<TARGET_IP>` (pw:msfadmin)

### Day 2 / 3
- [ ] `msfconsole --version`
- [ ] `ss -tlnp | grep 55553` (RPC daemon running)
- [ ] `attackmate --config config.yml --version` (config parses)

### Day 4 — Bettercap
- [ ] `bettercap --version`
- [ ] REST API accessible: `curl -u btrcp:secret http://127.0.0.1:8081/api/v1/session`

### Day 4 — Browser
- [ ] `uv run playwright install chromium`
- [ ] `uv run python -c "from playwright.sync_api import sync_playwright; print('OK')"`
