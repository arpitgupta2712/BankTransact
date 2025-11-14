# Bank Statement Consolidation Web App

A simple, user-friendly web interface for consolidating bank statements from HDFC and AXIS banks.

## Features

- 🎯 **Drag & Drop Interface**: Easy file upload with drag-and-drop support
- 🏦 **Multi-Bank Support**: Separate interfaces for HDFC and AXIS banks
- 📊 **Real-time Processing**: Live status updates during processing
- 📥 **Download Results**: Download consolidated CSV and summary reports
- 🎨 **Modern UI**: Clean, responsive design

## Quick Start

### 1. Start the Web Server

```bash
cd web
./run.sh
```

Or manually:

```bash
cd web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### 2. Open in Browser

The app will automatically find an available port (usually 5001 to avoid macOS AirPlay). 
Check the terminal output for the exact URL, or try: **http://localhost:5001**

### 3. Choose Your Bank

- **HDFC Bank**: For Excel files (.xls, .xlsx)
- **AXIS Bank**: For CSV files (.csv, .txt)

### 4. Upload and Process

1. Drag and drop your statement files or click to browse
2. Click "Process Statements"
3. Wait for processing to complete
4. Download the consolidated CSV and summary report

## File Formats

### HDFC Bank
- **Supported**: `.xls`, `.xlsx` (Excel files)
- **Source**: HDFC bank statement Excel exports

### AXIS Bank
- **Supported**: `.csv`, `.txt` (CSV files)
- **Source**: AXIS bank statement CSV exports

## Project Structure

```
web/
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── run.sh                 # Startup script
├── templates/            # HTML templates
│   ├── index.html        # Main page
│   ├── hdfc.html         # HDFC processing page
│   └── axis.html         # AXIS processing page
├── uploads/              # Temporary upload directory (auto-created)
└── outputs/              # Processed files directory (auto-created)
```

## API Endpoints

- `GET /` - Main index page
- `GET /hdfc` - HDFC bank processing page
- `GET /axis` - AXIS bank processing page
- `POST /api/upload/<bank_type>` - Upload files
- `POST /api/process/<bank_type>` - Process statements
- `GET /api/download/<filename>` - Download processed files
- `POST /api/cleanup/<session_id>` - Clean up session files

## Technical Details

### Backend
- **Framework**: Flask
- **Python**: 3.9+
- **Dependencies**: pandas, openpyxl, xlrd, numpy

### Frontend
- **Pure HTML/CSS/JavaScript**: No frameworks required
- **Drag & Drop**: Native HTML5 File API
- **Responsive**: Works on desktop and mobile

## Troubleshooting

### Port Already in Use
The app automatically finds a free port starting from 5001. If you need a specific port, modify `app.py`:
```python
port = find_free_port(8080)  # Start from port 8080
```

### Import Errors
Make sure you're running from the project root and the HDFC/AXIS modules are accessible:
```bash
# From BankTransact directory
cd web
python3 app.py
```

### File Upload Issues
- Check file size (max 100MB per file)
- Ensure file extensions match (.xls/.xlsx for HDFC, .csv/.txt for AXIS)
- Check browser console for errors

## Security Notes

- This is a local development server
- Files are stored temporarily in `uploads/` and `outputs/` directories
- Consider adding authentication for production use
- Clean up old files periodically

## License

Same as main BankTransact project (MIT License)

