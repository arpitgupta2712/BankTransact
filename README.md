# BankTransact - Bank Statement Processing Suite

A comprehensive web-based solution for processing and analyzing bank statements from multiple banks (AXIS and HDFC), featuring intelligent categorization, vendor detection, and detailed financial analytics.

## 🏗 Architecture

This is a **Flask web application** with a clear separation of concerns:

```
BankTransact/
├── requirements.txt      # 📦 Single unified dependencies file
├── start.sh              # 🚀 Start script
│
├── src/                  # 🔧 Backend Business Logic
│   ├── HDFC/            # HDFC bank processor
│   └── AXIS/             # AXIS bank processor
│
└── web/                  # 🌐 Flask Web Application
    ├── app.py           # Flask server (API + serves frontend)
    ├── templates/       # Frontend HTML templates
    ├── uploads/         # Temporary uploads
    └── outputs/         # Processed files
```

**Why this structure?**
- `src/` = Pure Python business logic (no web dependencies)
- `web/` = Flask app that serves both:
  - **Backend API**: REST endpoints in `app.py`
  - **Frontend**: HTML templates in `templates/`
- This is the **standard Flask pattern** - one app serves both API and UI

## 🚀 Quick Start

### Start the Web App

From the project root:
```bash
./start.sh
```

Then open `http://localhost:5001` in your browser.

### Usage Steps

1. **Choose Bank Type**
   - Click "HDFC Bank" for Excel files (.xls, .xlsx)
   - Click "AXIS Bank" for CSV files (.csv, .txt)

2. **Upload Files**
   - Drag and drop statement files or click to browse
   - Upload multiple files at once

3. **Configure (HDFC only)**
   - Click "Show/Hide" in Account Mapping Configuration
   - Update account mappings if needed
   - Click "Save Configuration"

4. **Process**
   - Click "Process Statements"
   - Wait for processing to complete

5. **Download Results**
   - Download consolidated CSV file
   - Download summary report

## ✨ Key Features

### Web Application
- **🌐 Modern Web Interface**: Accessible from any device
- **🎯 Drag & Drop Upload**: Easy file upload
- **⚙️ Account Configuration**: Configure mappings via web UI (HDFC)
- **📊 Real-time Processing**: Live status updates
- **📥 Download Results**: Download CSV and summary reports

### Intelligent Categorization (HDFC)
- **Main Categories**: Primary Revenue, Personnel Costs, Operating Expenses, Cost of Revenue, Capital Expenditure, Financing Activities, Statutory Payments
- **Smart Vendor Detection**: Extracts vendor names from transactions
- **Flexible Configuration**: Update account mappings without code changes

### Advanced Analytics
- **Transaction Classification**: Separate income and expense
- **Inter-bank Detection**: Identify transfers between accounts
- **Reversal Detection**: Detect cancelled/failed transactions
- **Party Analysis**: Extract and categorize party names (AXIS)

## 📁 Project Structure

```
BankTransact/
├── requirements.txt      # 📦 All dependencies (Flask, pandas, etc.)
├── start.sh              # 🚀 Start web app
│
├── src/                  # 🔧 Backend Business Logic
│   ├── HDFC/            # 🏦 HDFC Bank Processing
│   │   ├── consolidate_statements.py
│   │   ├── enhance_transactions.py
│   │   └── account_config.json
│   └── AXIS/            # 🏦 AXIS Bank Processing
│       ├── run_complete_workflow.py
│       ├── consolidate_statements.py
│       ├── party_analysis.py
│       └── create_party_summary.py
│
└── web/                  # 🌐 Flask Web Application
    ├── app.py           # Flask server (API endpoints)
    ├── templates/       # Frontend HTML/CSS/JS
    │   ├── index.html
    │   ├── hdfc.html
    │   └── axis.html
    ├── uploads/         # Temporary uploads (auto-cleaned)
    └── outputs/         # Processed files (auto-cleaned)
```

## ⚙️ Configuration

### Account Mapping (HDFC)

**Location**: `src/HDFC/account_config.json`

**Format**:
```json
{
  "account_mapping": {
    "05722560003098": "Main",
    "99909910666666": "Infra",
    "99909910777777": "Sports",
    "99909910888888": "Employees"
  }
}
```

**Update via**:
1. Web UI: Account Mapping Configuration section
2. Manual: Edit `src/HDFC/account_config.json`
3. API: `GET/POST /api/config/hdfc/account-mapping`

## 📊 Output Files

### HDFC Processing
- `consolidated_bank_statements.csv` - Merged statement data
- `consolidated_bank_statements_enhanced.csv` - With categorization and vendor names
- `consolidation_summary.txt` - Processing summary

### AXIS Processing
- `consolidated_axis_statements.csv` - Merged statement data
- `axis_income_transactions.csv` - Income analysis
- `axis_income_with_parties.csv` - Income with party categorization
- `party_list_summary.csv` - Party analysis summary
- `consolidation_summary.txt` - Processing summary

## 🔧 Technical Details

### Requirements
- **Python**: 3.9+
- **Dependencies**: See `requirements.txt` (Flask, pandas, openpyxl, xlrd, numpy)
- **Browser**: Modern browser with JavaScript

### File Formats
- **HDFC**: `.xls`, `.xlsx` (Excel files)
- **AXIS**: `.csv`, `.txt` (CSV files)

### API Endpoints
- `GET /` - Main index page
- `GET /hdfc` - HDFC processing page
- `GET /axis` - AXIS processing page
- `POST /api/upload/<bank_type>` - Upload files
- `POST /api/process/<bank_type>` - Process statements
- `GET /api/download/<filename>` - Download files
- `GET /api/config/hdfc/account-mapping` - Get account mapping
- `POST /api/config/hdfc/account-mapping` - Update account mapping
- `POST /api/cleanup/<session_id>` - Clean up session

## 🛠 Command Line Usage (Alternative)

```bash
# HDFC Bank Processing
cd src/HDFC
python3 consolidate_statements.py

# Enhanced Analysis (HDFC)
python3 enhance_transactions.py consolidated_statements.csv

# AXIS Bank Processing
cd src/AXIS
python3 run_complete_workflow.py
```

## 🔒 Security & Privacy

- **Local Processing**: All data processed locally
- **No Network Access**: No external data transmission
- **Temporary Cleanup**: Automatic cleanup of uploaded files
- **Git Ignored**: Sensitive files excluded from version control

## ⚠️ Troubleshooting

### Port Already in Use
App automatically finds free port starting from 5001.

### Import Errors
Run `./start.sh` from project root - it handles all setup automatically.

### File Upload Issues
- Max file size: 100MB
- File extensions: .xls/.xlsx for HDFC, .csv/.txt for AXIS
- Check browser console (F12) for errors

## 🚀 Development

### Adding New Banks
1. Create bank directory in `src/`
2. Implement processor in `src/<BANK>/consolidate_statements.py`
3. Add routes to `web/app.py`
4. Create template in `web/templates/`
5. Update account config if needed

### Code Structure
- **Backend Logic**: `src/` - Pure Python, no web dependencies
- **Web Server**: `web/app.py` - Flask API endpoints
- **Frontend**: `web/templates/` - HTML/CSS/JavaScript
- **Configuration**: JSON files in bank directories

---

**Built with ❤️ using Flask, Python, and modern web technologies**
