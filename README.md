# PowerSense - Full Stack Power Analysis System

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run the Backend Server
```bash
python app.py
```

The server will start at `http://localhost:5000`

#### 3. Access the Web App
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📊 Features

### Advanced ML Algorithms
✅ **Z-Score & Isolation Forest** - Robust anomaly detection  
✅ **ARIMA** - Time-series forecasting (10-step ahead prediction)  
✅ **Fourier Transform** - Cyclic pattern detection  
✅ **Markov Chains** - State transition modeling  
✅ **Linear Regression** - Trend analysis  
✅ **Stability Scoring** - System health assessment (0-100)  

### Backend Services
✅ **Flask REST API** - All operations via HTTP endpoints  
✅ **SQLite Database** - Persistent storage for all sessions  
✅ **Session Management** - Save, load, delete analyses  
✅ **Cost Analysis** - Daily/monthly electricity cost estimation  
✅ **Recommendations** - Actionable insights based on patterns  

### Frontend
✅ **Multi-Page App** - Dashboard, History, About  
✅ **Real-Time Charts** - Chart.js visualizations  
✅ **Drag & Drop Upload** - Easy file import  
✅ **Export Options** - CSV and JSON formats  
✅ **Responsive Design** - Works on desktop & mobile  

---

## 📁 Project Structure

```
webapp/
├── app.py                    # Flask backend
├── models.py                 # Database models
├── ml_service.py             # ML algorithms & analysis
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Main multi-page UI
├── static/                  # (CSS/JS files if needed)
└── powersense.db            # SQLite database (auto-created)
```

---

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns: `{"status": "ok", "service": "PowerSense Backend v2.0"}`

### Upload & Analyze
```
POST /api/upload
```
**Form Data:**
- `file`: Log file (CSV/TXT)
- `session_name`: Name for this session
- `tariff`: Cost per kWh (₦)
- `wattage`: Appliance wattage (W, optional)

**Returns:** Full analysis with all ML results

### Get All Sessions
```
GET /api/history
```
Returns: List of all saved sessions

### Get Session Details
```
GET /api/session/{id}
```
Returns: Session data + readings + analysis

### Delete Session
```
DELETE /api/session/{id}
```

### Export Session
```
GET /api/export/{id}?format=csv|json
```
Downloads file in requested format

### Get Recommendations
```
GET /api/recommendations/{id}
```
Returns: Actionable recommendations for session

### Get Forecast
```
GET /api/forecast/{id}
```
Returns: 10-step ARIMA forecast

---

## 📊 File Format

Your power log file should contain values (one per line):

**Simple Format:**
```
2.48
2.49
2.50
2.49
...
```

**With Timestamps:**
```
10:30:15 2.48
10:30:16 2.49
10:30:17 2.50
10:30:18 2.49
...
```

---

## 🎯 Using the Application

### 1. Dashboard (Analyze)
- Upload a power log file
- Set electricity tariff (default: ₦68/kWh)
- Set appliance wattage (optional, for accurate cost calc)
- Click "Analyse"
- View:
  - Real-time charts
  - 10-step forecast
  - Anomalies detected
  - Cost estimates
  - Recommendations
  - Export results

### 2. History
- View all past analyses
- Click "View" to re-examine results
- Click "Delete" to remove sessions

### 3. About
- Learn about algorithms used
- Feature overview
- Getting started guide

---

## 🔧 Configuration

Edit `app.py` to change:
- **Database**: Line 11 (`SQLALCHEMY_DATABASE_URI`)
- **Port**: Line 337 (default: 5000)
- **Debug Mode**: Line 337 (default: True)

---

## 📈 Analysis Output

Each analysis produces:

```json
{
  "global_stats": {
    "mean": 2.49,
    "std": 0.004,
    "min": 2.48,
    "max": 2.50,
    ...
  },
  "zscore_anomalies": [...],
  "isolation_forest_anomalies": [...],
  "fourier_analysis": {...},
  "trend_analysis": {
    "slope": -0.00001,
    "trend": "stable"
  },
  "forecast": {
    "forecast": [2.49, 2.49, ...],
    "method": "ARIMA"
  },
  "stability_score": 95.7,
  "cost_analysis": {
    "session_kwh": 0.0034,
    "daily_cost": 0.23,
    "monthly_cost": 6.9
  },
  "recommendations": [...]
}
```

---

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
Edit line 337 in `app.py`:
```python
app.run(debug=True, host='localhost', port=5001)  # Use 5001 instead
```

### Error: "Database locked"
The database file might be corrupted. Delete it and restart:
```bash
rm powersense.db
python app.py
```

### Forecast not working (ARIMA)
The system falls back to exponential smoothing if ARIMA fails. This is normal for small datasets.

---

## 📦 Deployment

### Local Network Access
Edit `app.py` line 337:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
Access from any computer: `http://<your-ip>:5000`

### Production Deployment
Replace the debug server with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📝 Example Workflow

1. **Collect power readings** from your device
2. **Export to CSV/TXT** (one value per line)
3. **Upload to PowerSense** at http://localhost:5000
4. **Review analysis**:
   - Check stability score
   - Examine anomalies
   - Review forecast
5. **Export results** to CSV or JSON
6. **Compare sessions** in History

---

## 🤝 Contributing

To add new algorithms:
1. Edit `ml_service.py`
2. Add method to `PowerAnalyzer` class
3. Call it in `full_analysis()` method
4. Results appear in analysis output

---

## 📞 Support

For issues or features, check:
- `/api/health` endpoint to verify backend is running
- Browser console (F12) for frontend errors
- Server logs in terminal window

---

## ⚖️ License

Open source - use freely for personal/commercial projects

---

**PowerSense v2.0** - Intelligent Energy Analysis System
