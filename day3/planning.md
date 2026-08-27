# Day 3 Planning - Full Attack Chain Lab

## Goal
 Participants take everything from days 1-2 and assemble a complete, automated attack chain against Metasploitable2 from scratch. The day shifts from instructor-guided walkthroughs to participant-driven lab work, with theory on Mitre Framework and Cyber Kill Chain in the morning.

---

## Morning Theory Block (~2 hours)

### Module 1: Cyber Kill Chain (lecture, ~45 min)

Lockheed Martin's 7-phase model as the frame for the day.

Phases:
1. **Reconnaissance** - Gather information about the target (nmap, service enumeration)
2. **Weaponization** - Prepare the exploit/payload (msf-payload, selecting modules)
3. **Delivery** - Deliver the payload/trigger to the target (webserv, exploit delivery)
4. **Exploitation** - Execute code on the target (vsftpd backdoor, Samba RCE, PHP-CGI)
5. **Installation** - Establish persistence (SSH key, cron, backdoor user)
6. **Command and Control (C2)** - Maintain channel to target (Meterpreter, Sliver beacon)
7. **Actions on Objectives** - Accomplish the goal (credential dump, data exfil, lateral movement)

Key narrative: day 1 (SSH bruteforce + foothold) hit phases 1, 4, 5; day 2 (payloads, Metasploit, C2) added phases 2, 3, 6, 7. run the full chain explicitly, planning and labeling each phase.

Map specific AttackMate commands to kill chain phases:
- Recon: `shell` (nmap, hydra), `regex` (parse nmap output)
- Weaponization: `msf-payload` (generate ELF), `shell` (msfvenom)
- Delivery: `webserv`, `httpclient`, `sftp`
- Exploitation: `msf-module`, `ssh` (weak creds)
- Installation: `sftp` (upload key), `msf-session` / `ssh` (write cron), `shell` (generate keypair)
- C2: `msf-session`, `sliver-session`
- Actions: `msf-session` (hashdump, download), `sftp` (exfil), `shell` (nc transfer)

### Module 2: MITRE ATT&CK (excursion, ~30 min)

The ATT&CK matrix is a more granular, technique-focused taxonomy maintained by MITRE. It is widely used for threat intelligence, detection engineering, and red team reporting.

Structure:
- **Tactics** (TA): the "why" - 14 top-level goals (Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact)
- **Techniques** (T): the "how" - named attack methods under each tactic
- **Sub-techniques** (T.NNN): more specific variants of a technique

Kill Chain vs. ATT&CK: Kill Chain is a linear progression; ATT&CK is a matrix (attackers can jump phases, revisit, use multiple techniques per tactic). They are complementary.

Technique mappings 
| ATT&CK ID | Technique | What we do |
|---|---|---|
| T1046 | Network Service Discovery | nmap scans |
| T1595.002 | Vulnerability Scanning | nmap -sV, service fingerprinting |
| T1190 | Exploit Public-Facing Application | vsftpd, Samba, PHP-CGI exploits |
| T1078 | Valid Accounts | SSH login with msfadmin creds |
| T1059.004 | Unix Shell | Shell sessions, bash commands |
| T1105 | Ingress Tool Transfer | webserv to deliver payload |
| T1098.004 | SSH Authorized Keys | Persistence via uploaded key |
| T1053.003 | Cron | Persistence via crontab |
| T1136.001 | Local Account | Create backdoor user |
| T1082 | System Information Discovery | sysinfo, hostname, uname |
| T1087.001 | Local Account Discovery | cat /etc/passwd |
| T1003.008 | /etc/passwd and /etc/shadow | Credential dumping |
| T1552.001 | Credentials In Files | find readable credential files |
| T1041 | Exfiltration Over C2 Channel | Meterpreter download |
| T1048.003 | Exfiltration Over Unencrypted Protocol | nc file transfer, sftp download |
| T1095 | Non-Application Layer Protocol | Meterpreter TCP channel |

Reference: https://attack.mitre.org/

### Module 3: Where Attacks Manifest in Logs (lecture/blue team perspective, ~30 min)

Purpose: give participants a defender's view of their own attacks. This makes the training more complete and helps them understand why certain techniques are noisy or stealthy.

Log sources on Metasploitable2 / Linux:
- `/var/log/auth.log` - SSH logins, sudo usage, PAM events
  - Brute force: many "Failed password for X from Y" lines in quick succession
  - Successful login: "Accepted password for X from Y"
  - Root login: "ROOT LOGIN on tty1" or "session opened for user root by"
- `/var/log/syslog` - general system events, daemon messages
- `/var/log/vsftpd.log` - FTP connections (if vsftpd logging is enabled)
  - Connection logs: "CONNECT: Client Y", login attempts
- Apache logs (if applicable):
  - `/var/log/apache2/access.log` - every HTTP request
  - PHP-CGI RCE creates an unusual request: `GET /?-d+allow_url_include%3D...`
  - Content-Type injection requests look anomalous
- Samba logs: `/var/log/samba/` - SMB connection and auth events
- Process creation (not logged by default on Metasploitable2, but visible in real environments via auditd or EDR):
  - A reverse shell spawning bash with no TTY is detectable via process tree
  - `/proc/<pid>/cmdline` can reveal what spawned what
- Network:
  - Unexpected outbound TCP connections on non-standard ports (4444, 4445, 31337) are a key IOC
  - Connection to attacker IP from victim IP on a high port = reverse shell callback

Blue team rules of thumb:
- Many failed logins followed by one success = brute force
- Outbound connection to unknown IP on high port = C2 channel / reverse shell
- New listening port suddenly appearing = backdoor or bind shell
- Unusual process names with no terminal = planted binary / implant
- Changes to `/etc/passwd`, `/etc/cron.d/`, `~/.ssh/authorized_keys` = persistence

Tool to demo log reading from attacker perspective: `msf-session` running `tail /var/log/auth.log` after gaining access.

---

## Lab: Full Attack Chain (~3-4 hours)

### Concept

Participants assemble a full attack chain as a modular AttackMate playbook. Each phase of the kill chain is represented by one or more include files. Participants choose one option per phase from a "menu" and wire them together in a top-level playbook.

### Attack Path Menu (modular options per phase)

#### Phase 1: Reconnaissance

**Option A: Full port scan + service detection (nmap)**
- `shell` command running nmap -sV
- Parse open ports with `regex`
- Store target IP in variable

**Option B: Targeted scan + parse (nmap + regex)**
- Scan specific ports relevant to Metasploitable2
- Use regex `findall` to extract open ports
- Use `only_if` to branch based on discovered services

#### Phase 2 + 3: Weaponization + Delivery (varies by entry point)

These are bundled with entry point options below since they differ significantly per exploit path.

#### Phase 4: Exploitation / Initial Access (choose one entry point)

**Entry A: vsftpd 2.3.4 backdoor (CVE-2011-2523)**
- Port 21, no credentials needed
- `msf-module`: `exploit/unix/ftp/vsftpd_234_backdoor`
- Result: root shell session
- Quiet delivery (no file dropped on disk)
- ATT&CK: T1190

**Entry B: SSH with weak credentials**
- Port 22, credentials msfadmin/msfadmin (known default)
- `shell`: hydra bruteforce (or just connect directly)
- `ssh`: session with msfadmin credentials
- Result: interactive SSH session as msfadmin
- ATT&CK: T1078

**Entry C: Samba usermap_script (CVE-2007-2447)**
- Port 139/445, no credentials
- `msf-module`: `exploit/multi/samba/usermap_script`
- Result: root shell session
- ATT&CK: T1190

**Entry D: PHP-CGI argument injection (CVE-2012-1823)**
- Port 80, Apache PHP-CGI on Metasploitable2
- Requires generating a reverse shell payload first
- `msf-payload`: generate ELF reverse shell
- `webserv`: serve it (background)
- `msf-module`: `exploit/multi/http/php_cgi_arg_injection` to RCE and download + exec payload
- `msf-module`: `exploit/multi/handler` to catch the callback
- Result: Meterpreter or shell session
- ATT&CK: T1190, T1105

**Entry E: UnrealIRCd backdoor (CVE-2010-2075)**
- Port 6667, no credentials
- `msf-module`: `exploit/unix/irc/unreal_ircd_3281_backdoor`
- Result: shell session (as daemon user, not root)
- ATT&CK: T1190
- Bonus: motivates privilege escalation step

#### Phase 5: Installation / Persistence (choose one or more)

**Persist A: SSH authorized key**
- Requires root or access to target user's home
- `shell`: generate keypair with ssh-keygen on attacker
- `sftp` or `msf-session`: upload public key to `~/.ssh/authorized_keys`
- Verify: SSH login with key
- ATT&CK: T1098.004

**Persist B: Backdoor cron job**
- Requires write access to /etc/cron.d/ or current user's crontab
- `msf-session` or `ssh`: write a cron entry
- ATT&CK: T1053.003

**Persist C: Create backdoor user**
- Requires root
- `msf-session` or `ssh`: `useradd -m -s /bin/bash backdoor; echo "backdoor:backdoor123" | chpasswd`
- ATT&CK: T1136.001

#### Phase 6: Command and Control

This is handled by the entry point choice: Meterpreter sessions (Metasploit) or SSH sessions cover C2 for today's exercise.

#### Phase 7: Actions on Objectives (choose one or more)

**Action A: System discovery**
- `msf-session` or `ssh`: sysinfo, hostname, id, ifconfig, ps aux
- ATT&CK: T1082, T1057

**Action B: Credential collection**
- Root sessions: `msf-session` running `cat /etc/shadow`
- Or `msf-module`: `post/linux/gather/hashdump`
- ATT&CK: T1003.008

**Action C: File discovery and local collection**
- `msf-session` or `ssh`: find sensitive files
  - `find / -name "*.conf" -readable 2>/dev/null`
  - `find /home -name "*.txt" 2>/dev/null`
- Store interesting paths in variables
- ATT&CK: T1005, T1083

**Action D: Exfiltration via SFTP**
- Requires SSH access
- `sftp`: download /etc/passwd, /etc/shadow, any collected files
- ATT&CK: T1048.003

**Action E: Exfiltration via Meterpreter download**
- `msf-session`: download command for specific files
- ATT&CK: T1041

**Action F: Read logs (demonstrate attacker awareness of blue team visibility)**
- `msf-session` or `ssh`: `tail /var/log/auth.log` - see your own brute force attempts
- `msf-session` or `ssh`: `tail /var/log/apache2/access.log` - see your own HTTP exploit
- Good debrief discussion prompt



