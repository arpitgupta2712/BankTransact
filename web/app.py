#!/usr/bin/env python3
"""
Flask Web Application for Bank Statement Consolidation
Supports both HDFC and AXIS bank statement processing
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import traceback

# Add parent directory to path to import consolidation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import consolidation processors
from HDFC.consolidate_statements import HDFCStatementProcessor
from AXIS.consolidate_statements import AXISStatementProcessor

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
            
            return jsonify({
                'success': True,
                'message': 'AXIS statements processed successfully',
                'output_file': output_filename,
                'summary_file': f'axis_summary_{session_id}.txt' if summary_output and summary_output.exists() else None
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

