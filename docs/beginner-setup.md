# Beginner Setup Guide

This is the slow version of the setup instructions.

It is for people who saw Odysseus, opened GitHub, and immediately found three
new words they did not want to learn today. The goal here is not to explain
programming. The goal is to get the app running, explain the words you need for
that, and help you avoid the most common wrong turns.

## What you are installing

Odysseus is not a normal double-click app yet. It is a self-hosted web app.

That means:

- you start it from a terminal
- it runs on your own computer
- you open it in a browser at a local address
- the local address is usually `http://localhost:7000` or `http://127.0.0.1:7860`

That browser URL does not mean the app is hosted by someone else. `localhost`
and `127.0.0.1` both mean "this computer".

## Which path should I use?

Pick one path and stick to it for the first install.

| If this sounds like you | Use this |
| --- | --- |
| You have an M-series MacBook | [MacBook, Apple Silicon](#macbook-apple-silicon) |
| You have Windows and want the native launcher | [Windows, native launcher](#windows-native-launcher) |
| You already know Docker or want bundled services | [Docker](#docker) |
| You are on Linux or an older Intel Mac | [Manual Python setup](#manual-python-setup) |

If you do not know what Docker is, do not start there unless someone is helping
you. It is useful, but it adds another thing to debug.

## Words you will see

### Terminal

The terminal is a text window where you type commands.

On macOS, open **Terminal**.

On Windows, open **Windows PowerShell** for the native launcher. Do not use Git
Bash for the PowerShell launcher command.

### GitHub

GitHub is where the project code lives.

The green **Code** button can download a ZIP, but the normal setup path uses
`git clone` instead. `git clone` downloads the project into a folder and keeps
it in the shape the setup scripts expect.

### Command

A command is a line you paste into the terminal and run with Enter.

Run commands one at a time. If a command fails, stop there and read the error
instead of pasting the next command.

### Folder

The terminal is always "inside" one folder. `cd odysseus` means "change into the
Odysseus folder".

If the terminal says it cannot find a file, you are often in the wrong folder.

## Before you start

Install the basics for your operating system.

### macOS

You need:

- Terminal
- Git, usually installed automatically when macOS prompts for command line tools
- Python 3.11 or newer

If the first `git` command opens an Apple prompt asking to install command line
tools, accept it, let it finish, then run the command again.

### Windows

You need:

- Windows PowerShell
- [Git for Windows](https://git-scm.com/download/win)
- Python 3.11 or newer

After installing Git or Python, close and reopen PowerShell before trying again.
That lets Windows refresh the command list.

## Download ZIP vs git clone

If you are new to GitHub, **Download ZIP** looks like the obvious button. For
this project, use `git clone` instead.

Reasons:

- setup commands in the README assume a cloned folder named `odysseus`
- cloning avoids a few Windows ZIP/archive false-positive problems
- it is easier to update later
- it makes help easier, because everyone is working from the same folder layout

The command is:

```bash
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
```

After that command finishes, move into the project folder:

```bash
cd odysseus
```

## About "virus detected" on the ZIP

If Windows Defender or another scanner blocks the GitHub ZIP, do not panic and
do not blindly disable your antivirus.

The usual cause is that source archives contain scripts. Security scanners can
flag scripts or unsigned launchers even when the project itself is not malware.
That does not mean every warning should be ignored. It means the ZIP path is a
bad first path for this repo.

Use the official repo URL with `git clone`:

```powershell
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
```

If your security tool flags a specific file after cloning, copy the exact file
name and warning into an issue. That is much more useful than only saying
"Windows says virus".

## MacBook, Apple Silicon

Use this if your Mac has an M1, M2, M3, M4, or newer Apple chip.

Open **Terminal** and run these commands one at a time:

```bash
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
cd odysseus
./start-macos.sh
```

The script handles the usual Mac setup work:

- installs Homebrew dependencies if needed
- creates a Python virtual environment
- runs the first setup
- starts the app on port `7860`

When it finishes, open:

```text
http://127.0.0.1:7860
```

On the first run, the terminal prints a temporary admin password. Use that
password to log in, then change it in Settings.

### If macOS says the script cannot run

Make sure you are inside the project folder:

```bash
pwd
```

The path should end with `odysseus`.

Then run:

```bash
chmod +x start-macos.sh
./start-macos.sh
```

### If port 7860 is already busy

Something else is using the port. You can start Odysseus on another port:

```bash
ODYSSEUS_PORT=7861 ./start-macos.sh
```

Then open:

```text
http://127.0.0.1:7861
```

## Windows, native launcher

Use this if you are on Windows and want the native launcher.

Open **Windows PowerShell**. Search for "PowerShell" in the Start menu.

Do not use Git Bash for this first run. Git Bash is useful, but the launcher
command below is a PowerShell command.

Run these commands one at a time:

```powershell
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
cd odysseus
powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
```

Important details:

- the file name is `launch-windows.ps1`
- there is a dot before `ps1`
- it is not `launch-windows-ps1`
- run the command from inside the `odysseus` folder

When the launcher finishes, open:

```text
http://localhost:7000
```

On the first run, the terminal prints a temporary admin password. Use that
password to log in, then change it in Settings.

### If PowerShell cannot find the script

Check your folder:

```powershell
pwd
```

The path should end with `odysseus`.

Then list the files:

```powershell
dir
```

You should see `launch-windows.ps1` in the list.

### If Python is not found

Install Python 3.11 or newer, then close and reopen PowerShell.

Check it with:

```powershell
py --version
```

If that prints a Python version, run the launcher again.

## Docker

Use this if you already have Docker Desktop installed, or if someone told you to
use Docker because you want the bundled services.

Open a terminal and run:

```bash
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
cd odysseus
cp .env.example .env
docker compose up -d --build
```

Open:

```text
http://localhost:7000
```

To see the startup logs:

```bash
docker compose logs -f odysseus
```

The first admin password is printed in those logs.

### If Docker says the daemon is not running

Open Docker Desktop and wait until it says Docker is running. Then retry the
`docker compose up -d --build` command.

### If port 7000 is already busy

Edit `.env` and set another port:

```text
APP_PORT=7001
```

Then recreate the container:

```bash
docker compose up -d --build
```

Open:

```text
http://localhost:7001
```

## Manual Python setup

Use this if the platform-specific launcher is not the right fit for your system.

```bash
git clone https://github.com/pewdiepie-archdaemon/odysseus.git
cd odysseus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m uvicorn app:app --host 127.0.0.1 --port 7000
```

Open:

```text
http://localhost:7000
```

On Windows, the manual venv activation command is different:

```powershell
venv\Scripts\Activate.ps1
```

## First login

On first setup, Odysseus creates an admin user.

The username is usually:

```text
admin
```

The password is printed in the terminal during setup. It is temporary. Log in
with it once, then change it in Settings.

If you used Docker, read the logs:

```bash
docker compose logs odysseus
```

Look for the line that mentions the admin password.

## Updating later

If you installed with `git clone`, updating starts like this:

```bash
cd odysseus
git pull
```

Then run the same launcher you used before.

Mac:

```bash
./start-macos.sh
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
```

Docker:

```bash
docker compose up -d --build
```

## Common mistakes

### Pasting every command at once

Paste one command, press Enter, wait for it to finish, then paste the next one.

If command 2 fails and you already pasted command 3, the terminal output gets
harder to understand.

### Running commands from the wrong folder

Most Odysseus commands must be run from inside the `odysseus` folder.

Use:

```bash
pwd
```

or on Windows:

```powershell
pwd
```

The path should end with `odysseus`.

### Using Git Bash for a PowerShell script

On Windows, open **Windows PowerShell** for:

```powershell
powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
```

If you use Git Bash, paths and script execution can behave differently.

### Typing `.ps1` as `-ps1`

This is easy to miss.

Correct:

```powershell
.\launch-windows.ps1
```

Wrong:

```powershell
.\launch-windows-ps1
```

### Opening the wrong URL

Docker and most native/manual installs use:

```text
http://localhost:7000
```

The Mac Apple Silicon launcher uses:

```text
http://127.0.0.1:7860
```

If you changed the port, use the port you chose.

### Not reading the terminal after setup

The first password is printed in the terminal. If you close the terminal before
reading it, start the app again and check the output.

## Safety notes

Odysseus can use powerful local tools. Treat it like an admin app.

- keep authentication enabled
- do not expose it directly to the public internet
- do not paste API keys into public issues or screenshots
- do not commit `.env`, `data/`, logs, uploads, or local databases
- if you bind it to your LAN, use a trusted private network or reverse proxy

For local testing on your own computer, `localhost` and `127.0.0.1` are the
right addresses.

## What to include when asking for help

If you open an issue, include:

- your operating system
- Mac chip type if you are on a Mac, for example M1, M2, Intel
- whether you used Mac launcher, Windows launcher, Docker, or manual Python
- the exact command you ran
- the last 30 lines from the terminal
- the URL you tried to open
- screenshots only if they do not show passwords, API keys, or private files

Good help request:

```text
OS: Windows 11
Install path: native launcher
Command: powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
Problem: PowerShell cannot find launch-windows.ps1
I ran pwd and it shows C:\Users\me, not C:\Users\me\odysseus
```

That gives people enough information to help without guessing.

## Quick checklist

Before posting an issue, check these:

- did you clone the repo instead of using Download ZIP?
- did you run `cd odysseus`?
- are you using the right terminal for your OS?
- did you copy the command exactly?
- did you open the right localhost URL?
- did you check the terminal for the first password?

If all of that looks right and it still fails, open an issue with the details
from the previous section.
