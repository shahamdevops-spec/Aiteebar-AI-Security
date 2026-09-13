# Aiteebar Batch Files Guide

This directory contains batch files for easy process management on Windows.

## Available Batch Files

### 1. **kill-cmd.bat** ⚡ (Emergency - Use First!)
**Fastest way to close stuck CMD windows**
```bash
kill-cmd.bat
```
- ✅ Instantly closes all CMD windows
- ✅ Best for stuck/frozen windows
- ✅ Just one click!

---

### 2. **close-all.bat** 🔴 (Nuclear Option)
**Force closes everything**
```bash
close-all.bat
```
Closes:
- ✅ All Node.js processes (frontend)
- ✅ All Python processes (backend)
- ✅ All CMD windows
- ✅ All PowerShell windows

---

### 3. **control-panel.bat** 🎮 (Full Control)
**Interactive menu for selective process management**
```bash
control-panel.bat
```

Options:
1. Close ALL processes
2. Close Backend only (Python)
3. Close Frontend only (Node)
4. Close CMD windows only
5. Close PowerShell only
6. Show running processes
7. Exit

---

### 4. **start-fresh.bat** 🚀 (Full Restart)
**Complete fresh start - closes all and starts everything**
```bash
start-fresh.bat
```

Does:
1. Close all existing processes
2. Start Backend (http://localhost:8000)
3. Seed demo users
4. Start Frontend (http://localhost:3000)
5. Display login credentials

---

## Quick Start

### If CMD windows won't close:
```bash
kill-cmd.bat
```

### To close everything:
```bash
close-all.bat
```

### For selective control:
```bash
control-panel.bat
```

### To start fresh:
```bash
start-fresh.bat
```

---

## Usage Tips

1. **Right-click** any .bat file → **"Run as administrator"** for best results
2. **Don't close the terminal** - let the batch file run to completion
3. **Demo credentials appear at the end** of start-fresh.bat
4. **If a window gets stuck**, just use kill-cmd.bat

---

## Troubleshooting

### "Access Denied" error?
- Right-click the .bat file
- Select "Run as administrator"

### Processes still running?
- Try `close-all.bat` instead
- Or manually run: `taskkill /F /IM node.exe`

### Frontend/Backend won't start?
- Use `kill-cmd.bat` first
- Then run `start-fresh.bat`

---

## Login After Starting

After running `start-fresh.bat`:

1. Go to **http://localhost:3000/login**
2. Click one of the demo credential buttons, or manually enter:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@aiteebar.ai | Admin@123 |
| Analyst | analyst@aiteebar.ai | Analyst@123 |
| Viewer | viewer@aiteebar.ai | Viewer@123 |

3. Click **Sign In** ✅

---

## Which One to Use?

| Situation | Use This |
|-----------|----------|
| CMD window won't close | `kill-cmd.bat` |
| Everything is frozen | `close-all.bat` |
| Want to be selective | `control-panel.bat` |
| Starting fresh | `start-fresh.bat` |
| Checking processes | `control-panel.bat` → Option 6 |

---

**Happy coding! 🚀**
