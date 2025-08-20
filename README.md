# BankTransact - Bank Statement Processing Suite

A comprehensive solution for processing and analyzing bank statements from multiple banks, featuring both Python backend scripts and a native macOS SwiftUI application.

## 🚀 Version 2.0.0 - Major Release

### ✨ What's New in v2.0.0
- **🎯 Native macOS App**: Complete SwiftUI application for seamless user experience
- **🔄 Multi-Bank Support**: Process AXIS and HDFC bank statements
- **📊 Advanced Analytics**: Party analysis, transaction categorization, and detailed reporting
- **⚡ Real-time Processing**: Live progress tracking with comprehensive debug output
- **📁 Smart File Management**: Integrated file viewer and desktop export functionality

## 🏗 Architecture

### Frontend: SwiftUI macOS App
- **Location**: `BankTransactApp/`
- **Framework**: SwiftUI for macOS
- **Features**: Native UI, real-time processing, file management
- **Documentation**: [BankTransactApp/README.md](BankTransactApp/README.md)

### Backend: Python Processing Scripts
- **AXIS Bank**: `AXIS/` - Complete workflow with party analysis
- **HDFC Bank**: `HDFC/` - Statement consolidation and analysis
- **Features**: Virtual environments, comprehensive reporting, data validation

## 📊 Processing Capabilities

### Statement Processing
- ✅ **Multi-file Consolidation**: Merge multiple statement files
- ✅ **Transaction Classification**: Separate income and expense transactions
- ✅ **Balance Verification**: Validate opening/closing balances
- ✅ **Data Validation**: Comprehensive error checking and reporting

### Advanced Analytics
- ✅ **Party Analysis**: Extract and categorize party names
- ✅ **Transaction Patterns**: Identify recurring transactions
- ✅ **Financial Summaries**: Generate detailed financial reports
- ✅ **Export Options**: Multiple output formats (CSV, TXT)

### Output Files Generated
- `consolidated_[bank]_statements.csv` - Merged statement data
- `[bank]_income_transactions.csv` - Income analysis
- `[bank]_income_with_parties.csv` - Party-categorized income
- `party_list_summary.csv` - Party analysis summary
- `consolidation_summary.txt` - Processing summary
- `party_wise_income_summary.txt` - Party analysis report

## 🛠 Quick Start

### Option 1: macOS App (Recommended)
1. **Open the App**: Launch `BankTransactApp/BankTransactApp.xcodeproj` in Xcode
2. **Build & Run**: Press ⌘+R to build and run
3. **Select Bank**: Choose AXIS or HDFC
4. **Upload Files**: Select your CSV statement files
5. **Process**: Click "Process Statements" and watch real-time progress
6. **View Results**: Check generated files in the app or on desktop

### Option 2: Command Line
```bash
# AXIS Bank Processing
cd AXIS
python3 run_complete_workflow.py

# HDFC Bank Processing
cd HDFC
python3 consolidate_statements.py
```

## 📁 Project Structure

```
BankTransact/
├── BankTransactApp/                    # 🎯 SwiftUI macOS Application
│   ├── BankTransactApp.xcodeproj/      # Xcode project
│   ├── BankTransactApp/                # App source code
│   └── README.md                       # App documentation
├── AXIS/                               # 🏦 AXIS Bank Processing
│   ├── run_complete_workflow.py        # Main workflow script
│   ├── consolidate_statements.py       # Statement consolidation
│   ├── party_analysis.py              # Party name analysis
│   ├── create_party_summary.py        # Party summary generation
│   ├── data/                          # Output directories
│   └── axis_env/                      # Python virtual environment
├── HDFC/                              # 🏦 HDFC Bank Processing
│   ├── consolidate_statements.py       # HDFC consolidation
│   ├── data/                          # Output directories
│   └── README.md                      # HDFC documentation
├── scripts/                           # 🔧 Utility scripts
│   ├── build_and_run.sh              # App build script
│   └── README.md                      # Scripts documentation
└── README.md                          # This file
```

## 🎯 Key Features

### SwiftUI App Features
- **Multi-Bank Support**: Process AXIS and HDFC statements
- **File Upload**: Drag & drop or select CSV files
- **Real-time Progress**: Live status updates and debug output
- **Integrated Viewer**: View and open generated files
- **Desktop Export**: Automatic file organization on desktop
- **Error Handling**: Comprehensive error reporting and recovery

### Python Script Features
- **Virtual Environments**: Isolated Python environments per bank
- **Data Validation**: Balance verification and transaction integrity
- **Party Analysis**: Advanced party name extraction and categorization
- **Comprehensive Reporting**: Detailed analysis and summary reports
- **Flexible Output**: Multiple file formats and export options

## 🔧 Technical Requirements

### macOS App
- **macOS**: 15.5+
- **Xcode**: 15.0+
- **Swift**: 5.5+

### Python Scripts
- **Python**: 3.11+
- **Dependencies**: pandas, numpy (installed in virtual environments)
- **Virtual Environments**: Pre-configured for each bank

## 📈 Performance Metrics

### Processing Speed
- **AXIS Bank**: ~5000 transactions in ~30 seconds
- **HDFC Bank**: ~2000 transactions in ~15 seconds
- **Party Analysis**: Real-time processing with live updates

### File Handling
- **Input**: Multiple CSV statement files
- **Output**: 8+ organized files per processing run
- **Storage**: Efficient local processing with desktop export

## 🔒 Security & Privacy

### Data Protection
- **Local Processing**: All data processed locally
- **No Network Access**: No external data transmission
- **File Permissions**: Secure file system access
- **Temporary Cleanup**: Automatic cleanup of temporary files

### App Security
- **Sandbox Configuration**: Development-optimized permissions
- **File System Access**: Controlled access to project directories
- **Process Isolation**: Secure Python script execution

## 🚀 Getting Started

### For Users
1. **Download**: Clone or download the repository
2. **Setup**: Follow the [BankTransactApp README](BankTransactApp/README.md)
3. **Run**: Launch the SwiftUI app and start processing

### For Developers
1. **Environment**: Set up Xcode and Python environments
2. **Build**: Build the SwiftUI app and test Python scripts
3. **Extend**: Add support for additional banks or features

## 🔄 Version History

### v2.0.0 (Current) - Major Release
- ✅ **Native macOS App**: Complete SwiftUI application
- ✅ **Multi-Bank Support**: AXIS and HDFC processing
- ✅ **Advanced Analytics**: Party analysis and categorization
- ✅ **Real-time Processing**: Live progress tracking
- ✅ **Integrated UI**: File management and viewer
- ✅ **Desktop Export**: Automatic file organization
- ✅ **Comprehensive Debug**: Real-time output monitoring

### v1.x.x (Previous)
- Python-only implementation
- Command-line interface
- Basic consolidation features
- Single-bank support

## 🤝 Contributing

### Development Guidelines
- **Swift**: Follow Swift coding conventions and MVVM architecture
- **Python**: Maintain virtual environments and dependency management
- **Documentation**: Update README files for new features
- **Testing**: Test both app and scripts before committing

### Adding New Banks
1. Create bank-specific directory with Python scripts
2. Set up virtual environment with required dependencies
3. Implement consolidation and analysis scripts
4. Add bank support to SwiftUI app
5. Update documentation and test thoroughly

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

### Troubleshooting
1. **App Issues**: Check debug output in terminal
2. **Python Scripts**: Verify virtual environment setup
3. **File Permissions**: Ensure proper file system access
4. **Performance**: Monitor system resources during processing

### Documentation
- [BankTransactApp README](BankTransactApp/README.md) - SwiftUI app details
- [HDFC README](HDFC/README.md) - HDFC bank processing
- [Scripts README](scripts/README.md) - Utility scripts

---

## 🎉 Success Story

**BankTransact v2.0.0** represents a major evolution from a Python-only solution to a comprehensive banking analysis suite with a native macOS application. The integration of SwiftUI frontend with Python backend provides users with:

- **Seamless Experience**: Native macOS app with familiar interface
- **Powerful Processing**: Advanced Python analytics and party analysis
- **Real-time Feedback**: Live progress tracking and debug output
- **Professional Output**: Organized files with comprehensive reporting

**Built with ❤️ using SwiftUI and Python**
