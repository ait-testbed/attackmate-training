# AttackMate Training

Four-day hands-on training curriculum for [AttackMate](https://ait-testbed.github.io/attackmate/main/index.html), an attack orchestration tool that automates cyber attack scenarios via YAML playbooks.

## Curriculum

**Day 1 -  Fundamentals**
Playbook structure, variables, shell commands, SSH/SFTP, regex parsing, conditionals, loops, and error handling. Exercises target a Metasploitable2 VM. Walkthroughs 1-3 run locally without a target.

**Day 2 - Payloads, Metasploit, and C2**
Metasploit integration (`msf-module`, `msf-session`, `msf-payload`), payload delivery via `webserv`, shell-to-Meterpreter upgrades, modular playbooks with `include`, and an introduction to Sliver C2. Requires `msfrpcd` running on the attacker machine.

**Day 3 - Full Kill Chain Lab**
No new syntax. Participants assemble a complete multi-phase attack chain (recon → initial access → privilege escalation → post-exploitation → persistence → exfiltration) by wiring together modular include files.

**Day 4 - Advanced Capabilities**
Browser automation via Playwright (`browser`), network-layer attacks via Bettercap, remote orchestration across multiple AttackMate instances, and adding custom command types and executors to the AttackMate source tree.

## Folder Structure

Each day follows the same layout:

```
dayN/
├── handout/        # Lecture reference material (Markdown → PDF)
├── walkthroughs/   # Fully annotated, runnable playbooks (instructor-led)
├── exercises/      # Playbooks with # TODO comments (participant work)
│   ├── includes/   # Reusable sub-playbooks (Day 3+)
│   └── solutions/  # Complete working versions of each exercise
└── config.yml      # AttackMate config file (Day 2+)
```

## Running Playbooks

```bash
# Basic
attackmate playbook.yml

# With debug output
attackmate --debug playbook.yml

# With config (required from Day 2 onward)
attackmate --config config.yml playbook.yml
```

Exercises use placeholders for the target IP the attacker IP, replace these before running.

## Lab Environment

- **Attacker machine**: AttackMate and all required tools pre-installed
- **Target**: Metasploitable2,  a deliberately vulnerable Linux VM
