# 🎮 SPARK Global Control System

SPARK now supports **global control from any terminal**! You can pause, unpause, mute, and control SPARK from any terminal session, not just the one running the main application.

## 🚀 **Quick Start**

### **1. Start SPARK**
```bash
cd robot_assistant
source venv/bin/activate
python src/main.py
```

### **2. Control SPARK from Any Terminal**
Open a **new terminal** (anywhere on your system) and use:

```bash
# Navigate to robot_assistant directory
cd /path/to/robot_assistant

# Control commands
./spark pause      # Pause SPARK voice processing
./spark unpause    # Resume SPARK voice processing
./spark mute       # Mute SPARK audio output
./spark unmute     # Unmute SPARK audio output
./spark reset      # Reset conversation state
./spark status     # Check SPARK's status
./spark quit       # Gracefully shut down SPARK
./spark help       # Show all available commands
```

## 🎯 **Available Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `pause` | Pause voice processing | `./spark pause` |
| `unpause` | Resume voice processing | `./spark unpause` |
| `resume` | Alias for unpause | `./spark resume` |
| `mute` | Mute audio output | `./spark mute` |
| `unmute` | Unmute audio output | `./spark unmute` |
| `reset` | Reset conversation | `./spark reset` |
| `quit` | Shut down SPARK | `./spark quit` |
| `exit` | Alias for quit | `./spark exit` |
| `status` | Check status | `./spark status` |
| `help` | Show help | `./spark help` |

## 🔧 **How It Works**

### **File-based Control System**
- SPARK monitors `data/spark_control.txt` for commands
- Any terminal can write commands to this file
- SPARK processes commands and clears the file
- Commands are processed every 500ms for responsiveness

### **Real-time Response**
- Commands are processed within 500ms
- SPARK immediately responds to control commands
- Status updates are shown in real-time
- Multiple terminals can send commands simultaneously

## 📱 **Use Cases**

### **1. Remote Control**
```bash
# From your laptop
ssh user@spark-server
cd robot_assistant
./spark pause    # Pause SPARK remotely
```

### **2. Multiple Control Points**
```bash
# Terminal 1: Run SPARK
python src/main.py

# Terminal 2: Monitor status
watch -n 1 './spark status'

# Terminal 3: Control SPARK
./spark pause
./spark unpause
```

### **3. Scripted Control**
```bash
#!/bin/bash
# automation.sh
cd robot_assistant
./spark pause
sleep 10
./spark unpause
```

## 🧪 **Testing the System**

### **Test Global Control**
```bash
# Terminal 1: Start SPARK with global control
python test_global_control.py

# Terminal 2: Test commands
./spark pause
./spark status
./spark unpause
./spark quit
```

### **Test from Different Locations**
```bash
# From anywhere on your system
cd /path/to/robot_assistant
./spark status
./spark pause
```

## ⚠️ **Important Notes**

### **File Permissions**
- Ensure the `data/` directory is writable
- The control script creates the directory if it doesn't exist
- Commands are processed as the user running SPARK

### **Command Processing**
- Commands are processed in order (FIFO)
- Each command is processed only once
- The control file is cleared after processing
- Invalid commands are ignored

### **Performance**
- Control checking adds minimal overhead (~500ms intervals)
- Commands are processed asynchronously
- No impact on voice processing performance

## 🎉 **Benefits**

✅ **Multi-terminal Control**: Control SPARK from any terminal  
✅ **Remote Management**: Control SPARK over SSH  
✅ **Scripted Automation**: Automate SPARK control  
✅ **Real-time Response**: Commands processed within 500ms  
✅ **Non-blocking**: No impact on main application performance  
✅ **Cross-platform**: Works on Linux, macOS, Windows (with bash)  

## 🔮 **Future Enhancements**

- **Network Control**: Control SPARK over network
- **Web Interface**: Web-based control panel
- **Mobile App**: Phone app for SPARK control
- **Voice Commands**: Voice-activated control
- **Scheduled Commands**: Time-based automation

---

**🎮 Now you can control SPARK from anywhere!** 🚀🤖✨
