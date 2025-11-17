#!/usr/bin/env python3
"""
Complete AXIS Bank Workflow Script
Handles the entire process from statement consolidation to party analysis
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import time

class AXISWorkflow:
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.data_dir = self.project_dir / "data"
        self.venv_dir = self.project_dir / "axis_env"
        # Requirements are now in project root
        self.requirements_file = self.project_dir.parent.parent / "requirements.txt"
        
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "="*80)
        print(f"🚀 {title}")
        print("="*80)
    
    def print_step(self, step, description):
        """Print a step with description"""
        print(f"\n📋 Step {step}: {description}")
        print("-" * 60)
    
    def check_python(self):
        """Check if Python is available"""
        self.print_step(1, "Checking Python Installation")
        
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Python found: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"❌ Python not found or not working: {e}")
            return False
    
    def setup_virtual_environment(self):
        """Setup Python virtual environment"""
        self.print_step(2, "Setting up Virtual Environment")
        
        # Check if venv already exists
        if self.venv_dir.exists():
            print(f"✅ Virtual environment already exists at: {self.venv_dir}")
            return True
        
        try:
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], 
                         check=True, capture_output=True)
            print(f"✅ Virtual environment created at: {self.venv_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get the Python executable from virtual environment"""
        if platform.system() == "Windows":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"
    
    def get_venv_pip(self):
        """Get the pip executable from virtual environment"""
        if platform.system() == "Windows":
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"
    
    def install_dependencies(self):
        """Install required Python packages"""
        self.print_step(3, "Installing Dependencies")
        
        venv_pip = self.get_venv_pip()
        
        if not venv_pip.exists():
            print(f"❌ Pip not found at: {venv_pip}")
            return False
        
        try:
            print("Installing pandas...")
            subprocess.run([str(venv_pip), "install", "pandas>=1.5.0"], 
                         check=True, capture_output=True)
            
            print("Installing numpy...")
            subprocess.run([str(venv_pip), "install", "numpy>=1.21.0"], 
                         check=True, capture_output=True)
            
            print("✅ Dependencies installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def check_statements_directory(self):
        """Check if statements directory exists and has files"""
        self.print_step(4, "Checking Statements Directory")
        
        statements_dir = self.data_dir / "statements"
        
        if not statements_dir.exists():
            print(f"❌ Statements directory not found: {statements_dir}")
            print("Please place your AXIS bank statement CSV files in the data/statements/ directory")
            return False
        
        csv_files = list(statements_dir.glob("*.CSV")) + list(statements_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"❌ No CSV files found in: {statements_dir}")
            print("Please place your AXIS bank statement CSV files in the data/statements/ directory")
            return False
        
        print(f"✅ Found {len(csv_files)} CSV files in statements directory:")
        for file in csv_files[:5]:  # Show first 5 files
            print(f"   - {file.name}")
        if len(csv_files) > 5:
            print(f"   ... and {len(csv_files) - 5} more files")
        
        return True
    
    def run_consolidation(self):
        """Run the bank statement consolidation"""
        self.print_step(5, "Running Bank Statement Consolidation")
        
        venv_python = self.get_venv_python()
        consolidation_script = self.project_dir / "consolidate_statements.py"
        
        if not consolidation_script.exists():
            print(f"❌ Consolidation script not found: {consolidation_script}")
            return False
        
        try:
            print("Starting consolidation process...")
            result = subprocess.run([str(venv_python), str(consolidation_script)], 
                                  check=True, capture_output=True, text=True)
            print("✅ Consolidation completed successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Consolidation failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def run_party_analysis(self):
        """Run the party analysis"""
        self.print_step(6, "Running Party Analysis")
        
        venv_python = self.get_venv_python()
        party_script = self.project_dir / "party_analysis.py"
        
        if not party_script.exists():
            print(f"❌ Party analysis script not found: {party_script}")
            return False
        
        try:
            print("Starting party analysis...")
            result = subprocess.run([str(venv_python), str(party_script)], 
                                  check=True, capture_output=True, text=True)
            print("✅ Party analysis completed successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Party analysis failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def create_party_summary(self):
        """Create the final party summary"""
        self.print_step(7, "Creating Party Summary")
        
        venv_python = self.get_venv_python()
        summary_script = self.project_dir / "create_party_summary.py"
        
        if not summary_script.exists():
            print(f"❌ Party summary script not found: {summary_script}")
            return False
        
        try:
            print("Creating party summary...")
            result = subprocess.run([str(venv_python), str(summary_script)], 
                                  check=True, capture_output=True, text=True)
            print("✅ Party summary created successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Party summary creation failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def show_results(self):
        """Show the generated results"""
        self.print_step(8, "Workflow Results")
        
        print("📁 Generated Files:")
        
        # Check for consolidated files
        consolidated_file = self.data_dir / "consolidated" / "consolidated_axis_statements.csv"
        if consolidated_file.exists():
            print("✅ Consolidated statements: data/consolidated/consolidated_axis_statements.csv")
        
        # Check for income/expense files
        income_file = self.data_dir / "income" / "axis_income_transactions.csv"
        if income_file.exists():
            print("✅ Income transactions: data/income/axis_income_transactions.csv")
        
        expense_file = self.data_dir / "expense" / "axis_expense_transactions.csv"
        if expense_file.exists():
            print("✅ Expense transactions: data/expense/axis_expense_transactions.csv")
        
        # Check for party analysis files
        party_summary_file = self.data_dir / "summary" / "party_wise_income_summary.txt"
        if party_summary_file.exists():
            print("✅ Party analysis report: data/summary/party_wise_income_summary.txt")
        
        party_list_file = self.data_dir / "summary" / "party_list_summary.txt"
        if party_list_file.exists():
            print("✅ Party list summary: data/summary/party_list_summary.txt")
        
        party_csv_file = self.data_dir / "income" / "party" / "party_list_summary.csv"
        if party_csv_file.exists():
            print("✅ Party CSV: data/income/party/party_list_summary.csv")
        
        enhanced_file = self.data_dir / "income" / "party" / "axis_income_with_parties.csv"
        if enhanced_file.exists():
            print("✅ Enhanced income data: data/income/party/axis_income_with_parties.csv")
        
        # Check for summary file
        summary_file = self.data_dir / "summary" / "consolidation_summary.txt"
        if summary_file.exists():
            print("✅ Consolidation summary: data/summary/consolidation_summary.txt")
        
        print(f"\n📂 All generated files are in: {self.data_dir}")
        print("🎉 Workflow completed successfully!")
    
    def copy_all_files_to_desktop(self):
        """Copy all generated files to desktop with organized directory structure"""
        self.print_step(9, "Copying All Files to Desktop")
        
        import shutil
        from datetime import datetime
        
        # Create desktop directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_dir = Path.home() / "Desktop" / f"axis_complete_workflow_{timestamp}"
        
        try:
            # Remove old desktop directory if it exists
            if desktop_dir.exists():
                shutil.rmtree(desktop_dir)
            
            # Create new desktop directory structure
            desktop_dir.mkdir(parents=True, exist_ok=True)
            (desktop_dir / "consolidated").mkdir(exist_ok=True)
            (desktop_dir / "income").mkdir(exist_ok=True)
            (desktop_dir / "income" / "party").mkdir(exist_ok=True)
            (desktop_dir / "expense").mkdir(exist_ok=True)
            (desktop_dir / "summary").mkdir(exist_ok=True)
            
            files_copied = 0
            
            # Copy consolidated files
            consolidated_file = self.data_dir / "consolidated" / "consolidated_axis_statements.csv"
            if consolidated_file.exists():
                shutil.copy2(consolidated_file, desktop_dir / "consolidated" / "consolidated_axis_statements.csv")
                files_copied += 1
                print(f"✅ Copied: consolidated/consolidated_axis_statements.csv")
            
            # Copy income files
            income_file = self.data_dir / "income" / "axis_income_transactions.csv"
            if income_file.exists():
                shutil.copy2(income_file, desktop_dir / "income" / "axis_income_transactions.csv")
                files_copied += 1
                print(f"✅ Copied: income/axis_income_transactions.csv")
            
            # Copy income party files
            party_enhanced_file = self.data_dir / "income" / "party" / "axis_income_with_parties.csv"
            if party_enhanced_file.exists():
                shutil.copy2(party_enhanced_file, desktop_dir / "income" / "party" / "axis_income_with_parties.csv")
                files_copied += 1
                print(f"✅ Copied: income/party/axis_income_with_parties.csv")
            
            party_csv_file = self.data_dir / "income" / "party" / "party_list_summary.csv"
            if party_csv_file.exists():
                shutil.copy2(party_csv_file, desktop_dir / "income" / "party" / "party_list_summary.csv")
                files_copied += 1
                print(f"✅ Copied: income/party/party_list_summary.csv")
            
            # Copy expense files
            expense_file = self.data_dir / "expense" / "axis_expense_transactions.csv"
            if expense_file.exists():
                shutil.copy2(expense_file, desktop_dir / "expense" / "axis_expense_transactions.csv")
                files_copied += 1
                print(f"✅ Copied: expense/axis_expense_transactions.csv")
            
            # Copy summary files
            consolidation_summary = self.data_dir / "summary" / "consolidation_summary.txt"
            if consolidation_summary.exists():
                shutil.copy2(consolidation_summary, desktop_dir / "summary" / "consolidation_summary.txt")
                files_copied += 1
                print(f"✅ Copied: summary/consolidation_summary.txt")
            
            party_summary_file = self.data_dir / "summary" / "party_wise_income_summary.txt"
            if party_summary_file.exists():
                shutil.copy2(party_summary_file, desktop_dir / "summary" / "party_wise_income_summary.txt")
                files_copied += 1
                print(f"✅ Copied: summary/party_wise_income_summary.txt")
            
            party_list_file = self.data_dir / "summary" / "party_list_summary.txt"
            if party_list_file.exists():
                shutil.copy2(party_list_file, desktop_dir / "summary" / "party_list_summary.txt")
                files_copied += 1
                print(f"✅ Copied: summary/party_list_summary.txt")
            
            print(f"\n🎉 Successfully copied {files_copied} files to desktop!")
            print(f"📁 Desktop location: {desktop_dir}")
            print(f"📂 Complete organized directory structure created!")
            
            return desktop_dir
            
        except Exception as e:
            print(f"❌ Error copying files to desktop: {e}")
            return None
    
    def run_complete_workflow(self):
        """Run the complete workflow"""
        self.print_header("AXIS BANK COMPLETE WORKFLOW")
        print(f"Project directory: {self.project_dir}")
        print(f"Data directory: {self.data_dir}")
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Run all steps
        steps = [
            ("Python Check", self.check_python),
            ("Virtual Environment", self.setup_virtual_environment),
            ("Dependencies", self.install_dependencies),
            ("Statements Check", self.check_statements_directory),
            ("Consolidation", self.run_consolidation),
            ("Party Analysis", self.run_party_analysis),
            ("Party Summary", self.create_party_summary),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Workflow failed at step: {step_name}")
                print("Please check the error messages above and try again.")
                return False
        
        # Final desktop copy with all files
        self.copy_all_files_to_desktop()
        
        self.show_results()
        return True

def main():
    """Main function"""
    workflow = AXISWorkflow()
    
    try:
        success = workflow.run_complete_workflow()
        if success:
            print("\n🎉 All done! Workflow completed successfully.")
            print("📁 Check your desktop for the organized output files.")
            print("✅ Exiting gracefully...")
        else:
            print("\n❌ Workflow failed. Please check the error messages above.")
            print("❌ Exiting with error...")
            exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user")
        print("⏹️  Exiting...")
        exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("❌ Exiting with error...")
        exit(1)

if __name__ == "__main__":
    main()
