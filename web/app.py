#!/usr/bin/env python3
"""
Flask Web Application for Bank Statement Consolidation
Supports both HDFC and AXIS bank statement processing
"""

import os
import sys
import shutil
import tempfile
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import traceback
import zipfile
from io import BytesIO

# Add parent directory to path to import consolidation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import consolidation processors
from src.HDFC.consolidate_statements import HDFCStatementProcessor
from src.AXIS.consolidate_statements import AXISStatementProcessor
from src.AXIS.party_analysis import PartyAnalyzer
from src.AXIS.create_party_summary import create_party_list

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['OUTPUT_FOLDER'] = Path(__file__).parent / 'outputs'

# Create necessary directories
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(parents=True, exist_ok=True)

# Allowed file extensions
HDFC_ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
AXIS_ALLOWED_EXTENSIONS = {'csv', 'txt'}

def allowed_file(filename, bank_type):
    """Check if file extension is allowed"""
    if bank_type == 'hdfc':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in HDFC_ALLOWED_EXTENSIONS
    elif bank_type == 'axis':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in AXIS_ALLOWED_EXTENSIONS
    return False

@app.route('/')
def index():
    """Main index page"""
    return render_template('index.html')

@app.route('/hdfc')
def hdfc_page():
    """HDFC bank processing page"""
    return render_template('hdfc.html')

@app.route('/axis')
def axis_page():
    """AXIS bank processing page"""
    return render_template('axis.html')

@app.route('/api/upload/<bank_type>', methods=['POST'])
def upload_files(bank_type):
    """Handle file uploads"""
    if bank_type not in ['hdfc', 'axis']:
        return jsonify({'error': 'Invalid bank type'}), 400
    
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    # Create temporary directory for this session
    session_id = request.form.get('session_id', 'default')
    temp_dir = app.config['UPLOAD_FOLDER'] / session_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename, bank_type):
            filename = secure_filename(file.filename)
            filepath = temp_dir / filename
            file.save(str(filepath))
            uploaded_files.append(str(filepath))
    
    if not uploaded_files:
        return jsonify({'error': 'No valid files uploaded'}), 400
    
    return jsonify({
        'success': True,
        'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
        'files': uploaded_files,
        'session_id': session_id
    })

@app.route('/api/process/<bank_type>', methods=['POST'])
def process_statements(bank_type):
    """Process bank statements"""
    if bank_type not in ['hdfc', 'axis']:
        return jsonify({'error': 'Invalid bank type'}), 400
    
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    statements_dir = app.config['UPLOAD_FOLDER'] / session_id
    
    if not statements_dir.exists():
        return jsonify({'error': 'No files found for processing'}), 400
    
    try:
        # Process based on bank type
        if bank_type == 'hdfc':
            processor = HDFCStatementProcessor(str(statements_dir))
            output_file = processor.create_consolidated_csv()
            
            if not output_file:
                return jsonify({'error': 'Failed to process HDFC statements'}), 500
            
            # HDFC processor returns the output file path
            if isinstance(output_file, str):
                output_file_path = Path(output_file)
            else:
                output_file_path = output_file
            
            # Move output file to output folder
            output_filename = f'hdfc_consolidated_{session_id}.csv'
            output_path = app.config['OUTPUT_FOLDER'] / output_filename
            if output_file_path.exists():
                shutil.copy2(str(output_file_path), str(output_path))
            
            # Also get summary file
            summary_file = statements_dir.parent / 'consolidation_summary.txt'
            summary_output = None
            if summary_file.exists():
                summary_output = app.config['OUTPUT_FOLDER'] / f'hdfc_summary_{session_id}.txt'
                shutil.copy2(str(summary_file), str(summary_output))
            
            return jsonify({
                'success': True,
                'message': 'HDFC statements processed successfully',
                'output_file': output_filename,
                'summary_file': f'hdfc_summary_{session_id}.txt' if summary_output and summary_output.exists() else None
            })
        
        elif bank_type == 'axis':
            processor = AXISStatementProcessor(str(statements_dir))
            # Set data_dir to statements_dir parent for output organization
            processor.data_dir = Path(statements_dir).parent
            output_file = processor.create_consolidated_csv()
            
            if not output_file:
                return jsonify({'error': 'Failed to process AXIS statements'}), 500
            
            # AXIS processor saves to consolidated_dir, get the actual path
            if isinstance(output_file, Path):
                output_file_path = output_file
            else:
                output_file_path = processor.consolidated_dir / 'consolidated_axis_statements.csv'
            
            # Move output file to output folder
            output_filename = f'axis_consolidated_{session_id}.csv'
            output_path = app.config['OUTPUT_FOLDER'] / output_filename
            if output_file_path.exists():
                shutil.copy2(str(output_file_path), str(output_path))
            
            # Also get summary file if exists
            summary_file = processor.summary_dir / 'consolidation_summary.txt'
            summary_output = None
            if summary_file.exists():
                summary_output = app.config['OUTPUT_FOLDER'] / f'axis_summary_{session_id}.txt'
                shutil.copy2(str(summary_file), str(summary_output))
            
            # Run party analysis if income transactions exist
            party_files = {}
            income_file = processor.income_dir / 'axis_income_transactions.csv'
            if income_file.exists():
                try:
                    print("\n🔍 Running party analysis...")
                    
                    # Run party analysis
                    analyzer = PartyAnalyzer(str(income_file))
                    analyzer.analyze_transactions()
                    
                    # Generate party summary
                    party_summary_file = analyzer.generate_party_summary(
                        str(processor.summary_dir / 'party_wise_income_summary.txt')
                    )
                    
                    # Create enhanced CSV with party names
                    enhanced_csv = analyzer.create_enhanced_csv(
                        str(processor.income_party_dir / 'axis_income_with_parties.csv')
                    )
                    
                    # Create party list summary
                    # Temporarily change working directory for create_party_list
                    original_cwd = os.getcwd()
                    os.chdir(str(processor.data_dir.parent))
                    party_list_txt, party_list_csv = create_party_list()
                    os.chdir(original_cwd)
                    
                    # Copy party analysis files to output folder
                    if party_summary_file and Path(party_summary_file).exists():
                        party_summary_output = app.config['OUTPUT_FOLDER'] / f'axis_party_summary_{session_id}.txt'
                        shutil.copy2(party_summary_file, str(party_summary_output))
                        party_files['party_summary'] = f'axis_party_summary_{session_id}.txt'
                    
                    if party_list_txt and Path(party_list_txt).exists():
                        party_list_output = app.config['OUTPUT_FOLDER'] / f'axis_party_list_{session_id}.txt'
                        shutil.copy2(party_list_txt, str(party_list_output))
                        party_files['party_list'] = f'axis_party_list_{session_id}.txt'
                    
                    if party_list_csv and Path(party_list_csv).exists():
                        party_list_csv_output = app.config['OUTPUT_FOLDER'] / f'axis_party_list_{session_id}.csv'
                        shutil.copy2(party_list_csv, str(party_list_csv_output))
                        party_files['party_list_csv'] = f'axis_party_list_{session_id}.csv'
                    
                    if enhanced_csv and Path(enhanced_csv).exists():
                        enhanced_csv_output = app.config['OUTPUT_FOLDER'] / f'axis_income_with_parties_{session_id}.csv'
                        shutil.copy2(enhanced_csv, str(enhanced_csv_output))
                        party_files['enhanced_csv'] = f'axis_income_with_parties_{session_id}.csv'
                    
                    print("✅ Party analysis completed successfully")
                except Exception as e:
                    print(f"⚠️ Party analysis failed: {e}")
                    traceback.print_exc()
                    # Continue even if party analysis fails
            
            return jsonify({
                'success': True,
                'message': 'AXIS statements processed successfully',
                'output_file': output_filename,
                'summary_file': f'axis_summary_{session_id}.txt' if summary_output and summary_output.exists() else None,
                'party_files': party_files if party_files else None
            })
    
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'error': f'Processing failed: {error_msg}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download processed files"""
    file_path = app.config['OUTPUT_FOLDER'] / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/download-party-reports/<session_id>')
def download_party_reports(session_id):
    """Download all party analysis reports as a ZIP file"""
    try:
        # Create a BytesIO object to store the ZIP file in memory
        memory_file = BytesIO()
        
        # Create ZIP file
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # List of possible party report files
            party_files = [
                (f'axis_party_list_{session_id}.txt', 'Party_List_Summary.txt'),
                (f'axis_party_list_{session_id}.csv', 'Party_List_Summary.csv'),
                (f'axis_party_summary_{session_id}.txt', 'Detailed_Party_Analysis.txt'),
                (f'axis_income_with_parties_{session_id}.csv', 'Income_With_Party_Names.csv')
            ]
            
            files_added = 0
            for filename, archive_name in party_files:
                file_path = app.config['OUTPUT_FOLDER'] / filename
                if file_path.exists():
                    zipf.write(file_path, archive_name)
                    files_added += 1
            
            if files_added == 0:
                return jsonify({'error': 'No party reports found'}), 404
        
        # Seek to the beginning of the BytesIO object
        memory_file.seek(0)
        
        # Send the ZIP file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'axis_party_reports_{session_id}.zip'
        )
    
    except Exception as e:
        print(f"Error creating ZIP file: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to create ZIP file: {str(e)}'}), 500

@app.route('/api/cleanup/<session_id>', methods=['POST'])
def cleanup_session(session_id):
    """Clean up temporary files for a session"""
    try:
        temp_dir = app.config['UPLOAD_FOLDER'] / session_id
        if temp_dir.exists():
            shutil.rmtree(str(temp_dir))
        
        # Also clean up output files for this session
        for file in app.config['OUTPUT_FOLDER'].glob(f'*_{session_id}.*'):
            file.unlink()
        
        return jsonify({'success': True, 'message': 'Session cleaned up'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/hdfc/account-mapping', methods=['GET'])
def get_account_mapping():
    """Get current account mapping configuration"""
    try:
        config_path = Path(__file__).parent.parent / 'src' / 'HDFC' / 'account_config.json'
        
        if not config_path.exists():
            return jsonify({
                'error': 'Config file not found',
                'account_mapping': {}
            }), 404
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return jsonify({
            'success': True,
            'account_mapping': config.get('account_mapping', {}),
            'description': config.get('description', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/hdfc/account-mapping', methods=['POST'])
def update_account_mapping():
    """Update account mapping configuration"""
    try:
        data = request.get_json()
        account_mapping = data.get('account_mapping', {})
        
        if not account_mapping:
            return jsonify({'error': 'account_mapping is required'}), 400
        
        config_path = Path(__file__).parent.parent / 'src' / 'HDFC' / 'account_config.json'
        
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new one
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update account mapping
        config['account_mapping'] = account_mapping
        config['description'] = data.get('description', config.get('description', 
            'Account number to account name mapping. Update this file to customize account names for different clients.'))
        
        # Save config file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Account mapping updated successfully',
            'account_mapping': account_mapping
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import socket
    
    def find_free_port(start_port=5001, max_attempts=10):
        """Find a free port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return None
    
    # Try to find a free port (starting from 5001 to avoid AirPlay on macOS)
    port = find_free_port(5001)
    if port is None:
        print("❌ Error: Could not find a free port")
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 Bank Statement Consolidation Web App")
    print("=" * 60)
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Output folder: {app.config['OUTPUT_FOLDER']}")
    print(f"🌐 Starting server on http://localhost:{port}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=port)

