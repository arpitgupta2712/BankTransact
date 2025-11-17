# BankTransact - Bank Statement Processing Suite

A comprehensive web-based solution for processing and analyzing bank statements from multiple banks (AXIS and HDFC), featuring intelligent categorization, vendor detection, and detailed financial analytics.

## 🚀 Quick Start

### Start the Web App

From the project root, simply run:
```bash
./start.sh
```

The app will:
- Set up the virtual environment automatically
- Install dependencies if needed
- Start the Flask server on an available port (usually 5001)
- Show you the URL to open in your browser

**Open in browser**: `http://localhost:5001`

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
- **🌐 Modern Web Interface**: Accessible from any device with a browser
- **🎯 Drag & Drop Upload**: Easy file upload interface
- **⚙️ Account Configuration**: Configure account mappings via web UI (HDFC)
- **📊 Real-time Processing**: Live status updates during processing
- **📥 Download Results**: Download consolidated CSV and summary reports
- **🔄 Session Management**: Automatic cleanup of temporary files

### Intelligent Categorization (HDFC)
- **Main Categories**: 
  - Primary Revenue (Venue Bookings, Online Booking Revenue)
  - Personnel Costs (Salaries, Bonuses, Reimbursements)
  - Operating Expenses (Software, Travel, Professional Fees)
  - Cost of Revenue (Venue Infrastructure, Maintenance)
  - Capital Expenditure (Vehicles, Equipment)
  - Financing Activities (Loans, Internal Transfers)
  - Statutory Payments (TDS, Tax Payments)
- **Smart Vendor Detection**: Extracts vendor names from NEFT, IMPS, TPT, POS transactions
- **Flexible Configuration**: Update account mappings without code changes

### Advanced Analytics
- **Transaction Classification**: Separate income and expense transactions
- **Inter-bank Detection**: Identify transfers between accounts
- **Reversal Detection**: Detect cancelled/failed transactions
- **Party Analysis**: Extract and categorize party names (AXIS)
- **Financial Summaries**: Generate detailed categorized financial reports

## 📁 Project Structure

```
BankTransact/
├── start.sh              # 🚀 Start web app (run from root)
├── web/                  # 🌐 Web Application
│   ├── app.py           # Flask backend server
│   ├── templates/       # HTML templates
│   ├── uploads/         # Temporary uploads (auto-cleaned)
│   └── outputs/         # Processed files (auto-cleaned)
└── src/                 # 📦 Source Code
    ├── HDFC/            # 🏦 HDFC Bank Processing
    │   ├── consolidate_statements.py
    │   ├── enhance_transactions.py
    │   └── account_config.json
    └── AXIS/            # 🏦 AXIS Bank Processing
        ├── run_complete_workflow.py
        ├── consolidate_statements.py
        ├── party_analysis.py
        └── create_party_summary.py
```

## ⚙️ Configuration

### Account Mapping (HDFC)

The account mapping configuration allows you to customize account names for different clients.

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

**Ways to Update**:
1. **Via Web Interface**: Use the "Account Mapping Configuration" section on the HDFC page
2. **Manually**: Edit `src/HDFC/account_config.json` directly
3. **Via API**: 
   - `GET /api/config/hdfc/account-mapping` - Get current mapping
   - `POST /api/config/hdfc/account-mapping` - Update mapping

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
- `party_wise_income_summary.txt` - Party analysis report

## 🔧 Technical Details

### Requirements
- **Python**: 3.9+
- **Flask**: 2.3.0+
- **Dependencies**: pandas, openpyxl, xlrd, numpy
- **Browser**: Modern browser with JavaScript enabled

### File Formats
- **HDFC**: `.xls`, `.xlsx` (Excel files)
- **AXIS**: `.csv`, `.txt` (CSV files)

### API Endpoints
- `GET /` - Main index page
- `GET /hdfc` - HDFC bank processing page
- `GET /axis` - AXIS bank processing page
- `POST /api/upload/<bank_type>` - Upload files
- `POST /api/process/<bank_type>` - Process statements
- `GET /api/download/<filename>` - Download processed files
- `GET /api/config/hdfc/account-mapping` - Get account mapping
- `POST /api/config/hdfc/account-mapping` - Update account mapping
- `POST /api/cleanup/<session_id>` - Clean up session files

## 🛠 Command Line Usage (Alternative)

If you prefer command line processing:

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
- **Session Management**: Files stored temporarily in `web/uploads/` and `web/outputs/`

## ⚠️ Troubleshooting

### Port Already in Use
The app automatically finds a free port starting from 5001. If needed, modify `web/app.py`:
```python
port = find_free_port(8080)  # Start from port 8080
```

### Import Errors
Make sure you're running `./start.sh` from the project root. The script handles all path setup automatically.

### File Upload Issues
- Check file size (max 100MB per file)
- Ensure file extensions match (.xls/.xlsx for HDFC, .csv/.txt for AXIS)
- Check browser console (F12) for errors
- Check terminal output for Python errors

### Files Not Processing
- Verify file formats match bank type
- Check that account mapping is configured (HDFC)
- Review terminal output for detailed error messages

## 🚀 Development

### Adding New Banks
1. Create bank directory in `src/`
2. Implement consolidation script
3. Add bank support to `web/app.py`
4. Create HTML template in `web/templates/`
5. Update account configuration if needed

### Code Structure
- **Backend**: Python scripts in `src/` directories
- **Web Server**: Flask app in `web/app.py`
- **Frontend**: Pure HTML/CSS/JavaScript in `web/templates/`
- **Configuration**: JSON config files in bank directories

## 📄 License

MIT License

---

**Built with ❤️ using Flask, Python, and modern web technologies**
