"""
Flask Backend for PowerSense
Run: python app.py
"""
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime
import numpy as np
import io
from models import db, Session, Reading, Analysis
from ml_service import PowerAnalyzer
import csv

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///powersense.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)
CORS(app)

# Create database tables
with app.app_context():
    db.create_all()

# ========== MAIN ROUTES ==========

@app.route('/')
def index():
    """Serve the main app"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'PowerSense Backend v2.0'})

@app.route('/api/upload', methods=['POST'])
def upload_and_analyze():
    """Upload log file, analyze, and store in database"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    session_name = request.form.get('session_name', f'Session_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    tariff = float(request.form.get('tariff', 68))
    wattage = float(request.form.get('wattage', 0))
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Parse file
        lines = file.read().decode('utf-8').split('\n')
        values, timestamps = parse_log_lines(lines)
        
        if not values:
            return jsonify({'error': 'No valid readings found in file'}), 400
        
        # Create session
        session = Session(session_name=session_name, file_name=file.filename)
        db.session.add(session)
        db.session.flush()  # Get session ID
        
        # Store readings
        for val, ts in zip(values, timestamps):
            reading = Reading(session_id=session.id, value=val, timestamp=ts)
            db.session.add(reading)
        
        db.session.commit()
        
        # Run analysis
        analyzer = PowerAnalyzer(values, timestamps)
        analysis_result = analyzer.full_analysis(
            tariff=tariff,
            wattage=wattage,
            session_hours=len(values) * 0.5 / 3600  # Assume 0.5s per reading
        )
        
        # Store analysis
        analysis = Analysis(session_id=session.id, analysis_data=analysis_result)
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session_id': session.id,
            'session_name': session.session_name,
            'reading_count': len(values),
            'analysis': analysis_result
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get all stored sessions"""
    sessions = Session.query.order_by(Session.created_at.desc()).all()
    return jsonify({
        'sessions': [s.to_dict() for s in sessions]
    }), 200

@app.route('/api/session/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session with all details"""
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    readings = [{'value': r.value, 'timestamp': r.timestamp} for r in session.readings]
    analysis = session.analysis.to_dict() if session.analysis else None
    
    return jsonify({
        'session': session.to_dict(),
        'readings': readings,
        'analysis': analysis
    }), 200

@app.route('/api/session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    db.session.delete(session)
    db.session.commit()
    return jsonify({'status': 'deleted'}), 200

@app.route('/api/export/<int:session_id>', methods=['GET'])
def export_session(session_id):
    """Export session as CSV"""
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    export_format = request.args.get('format', 'csv')
    
    if export_format == 'json':
        data = {
            'session': session.to_dict(),
            'readings': [{'value': r.value, 'timestamp': r.timestamp} for r in session.readings],
            'analysis': session.analysis.analysis_data if session.analysis else None
        }
        output = io.BytesIO()
        output.write(json.dumps(data, indent=2).encode())
        output.seek(0)
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'session_{session_id}_export.json'
        )
    else:  # CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Reading #', 'Value (V)', 'Timestamp'])
        
        for i, reading in enumerate(session.readings, 1):
            writer.writerow([i, reading.value, reading.timestamp or 'N/A'])
        
        # Add analysis summary
        if session.analysis:
            writer.writerow([])
            writer.writerow(['ANALYSIS SUMMARY'])
            analysis = session.analysis.analysis_data
            writer.writerow(['Mean', analysis['global_stats']['mean']])
            writer.writerow(['Std Dev', analysis['global_stats']['std']])
            writer.writerow(['Min', analysis['global_stats']['min']])
            writer.writerow(['Max', analysis['global_stats']['max']])
            writer.writerow(['Stability Score', analysis['stability_score']])
            writer.writerow(['Monthly Cost', f"₦{analysis['cost_analysis']['monthly_cost']:.2f}"])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'session_{session_id}_export.csv'
        )

@app.route('/api/recommendations/<int:session_id>', methods=['GET'])
def get_recommendations(session_id):
    """Get recommendations for a session"""
    session = Session.query.get(session_id)
    if not session or not session.analysis:
        return jsonify({'error': 'Session or analysis not found'}), 404
    
    recommendations = session.analysis.analysis_data.get('recommendations', [])
    return jsonify({'recommendations': recommendations}), 200

@app.route('/api/forecast/<int:session_id>', methods=['GET'])
def get_forecast(session_id):
    """Get forecast for a session"""
    session = Session.query.get(session_id)
    if not session or not session.analysis:
        return jsonify({'error': 'Session or analysis not found'}), 404
    
    forecast = session.analysis.analysis_data.get('forecast', {})
    return jsonify({'forecast': forecast}), 200

# ========== UTILITY FUNCTIONS ==========

def parse_log_lines(lines):
    """Parse log file lines"""
    values = []
    timestamps = []
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                val = float(parts[1])
                values.append(val)
                timestamps.append(parts[0])
            except:
                pass
        elif len(parts) == 1:
            try:
                val = float(parts[0])
                values.append(val)
                timestamps.append(None)
            except:
                pass
    
    return values, timestamps

# ========== RUN SERVER ==========

if __name__ == '__main__':
    print("🚀 PowerSense Backend starting...")
    print("📊 Visit http://localhost:5000 for API docs")
    print("💾 Database: sqlite:///powersense.db")
    app.run(debug=False, host='0.0.0.0', port=5000)
