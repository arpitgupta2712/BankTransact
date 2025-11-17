# How to Restart the Server

## 🚀 Quick Restart

### Method 1: Using the start script (Recommended)

```bash
# From project root directory
cd /Users/arpitgupta/Downloads/apps/Concepts/personal/BankTransact
./start.sh
```

### Method 2: Manual restart

```bash
# 1. Stop the server (if running)
# Press Ctrl+C in the terminal where server is running
# OR kill the process:
pkill -f "python.*app.py"

# 2. Start the server
cd /Users/arpitgupta/Downloads/apps/Concepts/personal/BankTransact
./start.sh
```

## 📋 Step-by-Step Guide

### Starting the Server

1. **Open Terminal**
2. **Navigate to project root**:
   ```bash
   cd /Users/arpitgupta/Downloads/apps/Concepts/personal/BankTransact
   ```
3. **Run start script**:
   ```bash
   ./start.sh
   ```
4. **Wait for output** - You'll see:
   ```
   🚀 Starting Bank Statement Consolidation Web App
   📦 Creating virtual environment... (if first time)
   🔧 Activating virtual environment...
   📥 Installing dependencies...
   🌐 Starting Flask server...
   🌐 Starting server on http://localhost:5001
   ```
5. **Open browser**: Go to `http://localhost:5001`

### Stopping the Server

**Option 1: Keyboard shortcut** (if server is in foreground)
- Press `Ctrl + C` in the terminal

**Option 2: Kill process** (if server is in background)
```bash
# Find the process
ps aux | grep "python.*app.py"

# Kill it (replace PID with actual process ID)
kill <PID>

# OR kill all Flask processes
pkill -f "python.*app.py"
```

**Option 3: Kill by port**
```bash
# Find what's using port 5001
lsof -ti:5001

# Kill it
kill $(lsof -ti:5001)
```

## 🔄 Restart Process

1. **Stop**: `Ctrl + C` or `pkill -f "python.*app.py"`
2. **Start**: `./start.sh`

## 💡 Tips

- **Keep terminal open**: The server runs in the terminal - keep it open
- **Check port**: If port 5001 is busy, the app will try 5002, 5003, etc.
- **View logs**: All server output appears in the terminal
- **Background mode**: To run in background, add `&` at the end:
  ```bash
  ./start.sh &
  ```

## 🐛 Troubleshooting

### Port already in use?
```bash
# Find what's using the port
lsof -i:5001

# Kill it
kill $(lsof -ti:5001)
```

### Server won't start?
```bash
# Check if Python is available
python3 --version

# Check if you're in the right directory
pwd  # Should show: .../BankTransact

# Try manual activation
cd web
source venv/bin/activate
python3 app.py
```

### Import errors?
```bash
# Make sure you're running from project root
cd /Users/arpitgupta/Downloads/apps/Concepts/personal/BankTransact
./start.sh
```

