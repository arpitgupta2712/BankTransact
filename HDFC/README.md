# HDFC Bank Statement Consolidator

A professional Python tool for consolidating and analyzing multiple HDFC bank statement Excel files. Provides comprehensive financial insights, transaction classification, and business intelligence for multiple accounts.

## 🚀 Key Features

### **Advanced Transaction Processing**
- **Multi-Format Support**: Handles both `.xls` and `.xlsx` HDFC bank statement formats
- **Automatic Data Extraction**: Intelligently parses account info, transactions, and balances
- **Smart Data Cleaning**: Standardizes dates, amounts, and removes formatting inconsistencies
- **Error-Resistant Processing**: Graceful handling of malformed or inconsistent data

### **Intelligent Transaction Classification**
- **Unique Transactions**: Standard income/expense transactions
- **Inter-bank Detection**: Automatically identifies transfers between your own accounts
- **Reversed Transaction Detection**: Flags failed/cancelled transactions within same account
- **Business Logic**: Excludes internal transfers from financial performance calculations

### **Comprehensive Financial Analysis**
- **Real Balance Tracking**: Uses actual opening/closing balances from statements
- **Account Performance**: Individual account income, expenses, and net changes
- **Portfolio Overview**: Total portfolio growth/decline across all accounts
- **Business Insights**: External-only transaction analysis for true business performance

### **Professional Reporting**
- **Detailed Console Output**: Real-time processing status and comprehensive summary
- **Text File Export**: Complete analysis saved as `consolidation_summary.txt`
- **Clean CSV Output**: Structured data ready for further analysis
- **Account Mapping**: Custom account names for better readability
- **Desktop Integration**: Automatic copying of outputs to timestamped desktop directory

### **Command Line Flexibility**
- **Dynamic Path Support**: Specify any directory containing Excel statement files
- **Flexible Output Options**: Control desktop copying and output locations
- **Validation & Error Handling**: Built-in checks for directory existence and file formats
- **Help Documentation**: Comprehensive command line help and usage examples

## 📊 Output Structure

### Consolidated CSV Columns
| Column | Description |
|--------|-------------|
| `serial_no` | Sequential transaction number |
| `account_number` | Bank account number |
| `account_name` | Custom mapped account name (Primary, Infra, Sports, etc.) |
| `date` | Transaction date (YYYY-MM-DD) |
| `narration` | Transaction description |
| `reference_number` | Transaction reference/check number |
| `transaction_type` | Income or Expense |
| `withdrawal_amount` | Debit amount |
| `deposit_amount` | Credit amount |
| `net_transaction` | Net amount (deposit - withdrawal) |
| `transaction_classification` | Unique, Inter-bank, or Reversed |

### Summary Report Sections
- **Processing Summary**: Files processed, transactions extracted, date ranges
- **Account Overview**: Account types, transaction distribution
- **Transaction Classification**: Breakdown by Unique/Inter-bank/Reversed
- **Financial Analysis**: External transactions only (excludes internal transfers)
- **Real Balance Changes**: Actual account balance movements
- **Key Business Insights**: Highest expense accounts, portfolio performance

## 🛠 Setup & Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation Steps

1. **Clone/Download the Repository**
   ```bash
   cd /path/to/your/finance/directory
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python3 -m venv finance_env
   source finance_env/bin/activate  # On macOS/Linux
   # finance_env\Scripts\activate   # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies
```
pandas>=2.0.0
openpyxl>=3.1.0
xlrd>=2.0.0
numpy>=1.20.0
```

## 📁 Project Structure

```
Finance/
├── consolidate_statements.py     # Main processing script
├── requirements.txt             # Python dependencies
├── .gitignore                  # Security exclusions
├── data/                       # Default data directory
│   ├── statements/            # Default location for Excel files
│   │   └── .gitkeep          # (Excel files excluded from git)
│   ├── consolidated_bank_statements.csv  # Output (excluded from git)
│   └── consolidation_summary.txt        # Report (excluded from git)
└── README.md                   # This documentation

# Desktop Output (when enabled)
~/Desktop/statement_consolidated_YYYYMMDD_HHMMSS/
├── consolidated_bank_statements.csv     # Copy of main output
└── consolidation_summary.txt           # Copy of detailed report
```

## 🎯 Command Line Options

The consolidator supports flexible command line arguments for different use cases:

```bash
python consolidate_statements.py [OPTIONS]
```

### Available Options

| Option | Description | Default |
|--------|-------------|----------|
| `--statements-dir PATH` | Directory containing Excel statement files | `./data/statements` |
| `--no-desktop-copy` | Skip copying files to desktop directory | False (copies by default) |
| `--help` | Show help message and exit | - |

### Usage Examples

```bash
# Basic usage with default settings (copies to desktop)
python consolidate_statements.py

# Use custom directory with desktop copy
python consolidate_statements.py --statements-dir /path/to/your/statements

# Process files without desktop copy
python consolidate_statements.py --no-desktop-copy

# Custom directory without desktop copy
python consolidate_statements.py --statements-dir ./my_statements --no-desktop-copy

# Show all available options
python consolidate_statements.py --help
```

## 🚀 Usage

### 1. **Prepare Your Data**
Place your HDFC bank statement Excel files in any directory:
```
Expected format: Acct_Statement_XXXXXXXX####_DDMMYYYY.xls
Default location: ./data/statements/
```

### 2. **Run the Consolidator**
```bash
# Activate virtual environment
source finance_env/bin/activate

# Basic usage (uses ./data/statements/, copies to desktop)
python consolidate_statements.py

# Or specify custom path
python consolidate_statements.py --statements-dir /path/to/statements
```

### 3. **Review Results**

**Local Output:**
- **Console Output**: Real-time processing and comprehensive summary
- **CSV File**: `consolidated_bank_statements.csv` (in parent directory of statements)
- **Detailed Report**: `consolidation_summary.txt` (in parent directory of statements)

**Desktop Copy** (enabled by default):
- **Timestamped Directory**: `~/Desktop/statement_consolidated_YYYYMMDD_HHMMSS/`
- **Both Files Copied**: CSV and summary text files for easy access
- **Organized Storage**: Each run creates a new timestamped directory

## 🔧 Configuration

### Account Mapping
The tool uses a configuration file (`account_config.json`) for account number to account name mapping. This allows you to easily customize account names for different clients without modifying the code.

**Configuration File Location**: `HDFC/account_config.json`

**Format**:
```json
{
  "account_mapping": {
    "50200087543792": "Primary",
    "99909999099865": "Infra",
    "99919999099866": "Sports",
    "99909999099867": "B2B",
    "99909999099868": "B2C",
    "99909999099869": "Employees",
    "50200109619138": "Primary"
  },
  "description": "Account number to account name mapping. Update this file to customize account names for different clients."
}
```

**Ways to Update Account Mapping**:
1. **Via Web Interface**: Use the "Account Mapping Configuration" section on the HDFC processing page to edit and save mappings directly in the browser.
2. **Manually Edit Config File**: Edit `HDFC/account_config.json` directly with your preferred text editor.
3. **Via API**: Use the REST API endpoints:
   - `GET /api/config/hdfc/account-mapping` - Get current mapping
   - `POST /api/config/hdfc/account-mapping` - Update mapping

The configuration is automatically loaded when processing statements, making it easy to switch between different client configurations.

### Processing Directory
You can specify any directory containing Excel statement files:

```bash
# Use default location (./data/statements/)
python consolidate_statements.py

# Use custom absolute path
python consolidate_statements.py --statements-dir /Users/username/Downloads/bank_statements

# Use relative path
python consolidate_statements.py --statements-dir ./my_statements
```

### Desktop Output
Control desktop copying behavior:

```bash
# Enable desktop copy (default)
python consolidate_statements.py

# Disable desktop copy
python consolidate_statements.py --no-desktop-copy
```

## 🔐 Security Features

- **Sensitive Data Excluded**: Bank statements and outputs are `.gitignore`d
- **Local Processing**: All data remains on your machine
- **No Cloud Dependencies**: Completely offline operation
- **Account Number Masking**: Sample data uses masked account numbers

## 📈 Business Intelligence

### What You Get
- **True Financial Performance**: Excludes internal transfers for accurate business metrics
- **Account-wise Analysis**: Individual account performance and trends
- **Transaction Insights**: Classification of transaction types and patterns
- **Portfolio Overview**: Real balance changes across all accounts
- **Operational Metrics**: Processing statistics and data quality indicators

### Use Cases
- **Business Accounting**: Clean data for accounting software import
- **Financial Planning**: Historical transaction analysis for budgeting
- **Tax Preparation**: Organized transaction records with proper classification
- **Audit Support**: Comprehensive transaction trails with source traceability
- **Investment Analysis**: Portfolio balance tracking and performance monitoring

## 🚨 Important Notes

- **Data Privacy**: Bank statements contain sensitive information - never commit to public repositories
- **Backup**: Keep original Excel files as primary records
- **Validation**: Always verify processed data against original statements
- **Updates**: Bank statement formats may change - tool may need updates

## 🛠 Troubleshooting

### Common Issues
- **Directory Not Found**: Use `--statements-dir` to specify correct path to Excel files
- **No Excel Files**: Ensure directory contains `.xls` or `.xlsx` HDFC statement files
- **File Format Errors**: Ensure files are genuine HDFC Excel statements
- **Date Parsing Issues**: Check for unusual date formats in source files
- **Missing Balances**: Some statements may have incomplete balance information
- **Account Mapping**: Unknown accounts will show as "Unknown" - update mapping as needed
- **Desktop Copy Issues**: Check desktop permissions if copy fails

### Error Handling
The tool includes comprehensive error handling and will:
- Skip problematic files and continue processing
- Provide detailed error messages
- Generate partial results when possible

## 📞 Support

For technical issues:
1. Check error messages in console output
2. Verify file formats and structure
3. Ensure all dependencies are installed
4. Review the consolidation summary for processing details

---

**Developed for secure, professional financial data analysis**  
*Compatible with HDFC Bank statement formats as of 2025*