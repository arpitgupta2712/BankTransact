# Quick Start Guide

## 🚀 Start the Web App

### Option 1: Using the startup script (Recommended)
```bash
cd web
./run.sh
```

### Option 2: Manual setup
```bash
cd web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## 🌐 Access the App

The app will automatically find an available port (usually 5001). 
Check the terminal output for the exact URL, or try: **http://localhost:5001**

## 📋 Usage Steps

1. **Choose Bank Type**
   - Click on "HDFC Bank" for Excel files (.xls, .xlsx)
   - Click on "AXIS Bank" for CSV files (.csv, .txt)

2. **Upload Files**
   - Drag and drop your statement files into the upload area
   - Or click the upload area to browse and select files
   - You can upload multiple files at once

3. **Process**
   - Click the "Process Statements" button
   - Wait for processing to complete (you'll see status updates)

4. **Download Results**
   - Once processing is complete, download links will appear
   - Download the consolidated CSV file
   - Download the summary report (if available)

## 📁 File Locations

- **Uploaded files**: `web/uploads/` (temporary, cleaned up automatically)
- **Processed files**: `web/outputs/` (available for download)

## ⚠️ Troubleshooting

### Port issues?
The app automatically finds a free port. If you see port errors, the app will try the next available port automatically.

### Import errors?
Make sure you're running from the `web/` directory and the parent directory structure is correct.

### Files not processing?
- Check that file extensions match (.xls/.xlsx for HDFC, .csv/.txt for AXIS)
- Check browser console (F12) for error messages
- Check terminal output for Python errors

## 🎯 Example Workflow

1. Start server: `./run.sh`
2. Open browser: http://localhost:5000
3. Click "HDFC Bank"
4. Drag 3 Excel statement files
5. Click "Process Statements"
6. Wait ~30 seconds
7. Download consolidated CSV
8. Done! ✅

