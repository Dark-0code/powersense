# PowerSense - System Architecture

## Overview
PowerSense is a full-stack power analysis system with:
- **Backend**: Flask REST API with SQLite database
- **Frontend**: Multi-page HTML5 SPA with Chart.js visualizations
- **ML/Analytics**: Advanced Python algorithms (ARIMA, Isolation Forest, Fourier)
- **Storage**: Persistent session & analysis history

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         templates/index.html (Multi-page SPA)        │   │
│  │  ┌──────────────┬──────────────┬──────────────┐     │   │
│  │  │ Dashboard    │ History      │ About        │     │   │
│  │  └──────────────┴──────────────┴──────────────┘     │   │
│  │  ┌──────────────────────────────────────────┐       │   │
│  │  │  Chart.js Visualizations                 │       │   │
│  │  │  - Line Chart (readings)                 │       │   │
│  │  │  - Distribution Chart                    │       │   │
│  │  │  - Forecast Chart                        │       │   │
│  │  └──────────────────────────────────────────┘       │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↑ (Fetch API calls)                            │
└──────────────┼────────────────────────────────────────────────┘
               │ JSON
               ↓
┌─────────────────────────────────────────────────────────────┐
│              Flask Backend (app.py)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              REST API Routes                          │   │
│  │  • POST /api/upload       → Analyze file             │   │
│  │  • GET /api/history       → List sessions            │   │
│  │  • GET /api/session/{id}  → Get session data         │   │
│  │  • GET /api/export/{id}   → Download results         │   │
│  │  • DELETE /api/session    → Remove session           │   │
│  │  • GET /api/recommendations → Get insights           │   │
│  │  • GET /api/forecast      → Get predictions          │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓ (Data Processing)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          ML Service (ml_service.py)                   │   │
│  │  ┌────────────────────────────────────────────┐      │   │
│  │  │   PowerAnalyzer Class                      │      │   │
│  │  │   • get_global_stats()                     │      │   │
│  │  │   • zscore_anomaly_detection()             │      │   │
│  │  │   • isolation_forest_detection()           │      │   │
│  │  │   • fourier_analysis()                     │      │   │
│  │  │   • arima_forecast()                       │      │   │
│  │  │   • get_trend_analysis()                   │      │   │
│  │  │   • build_transition_matrix()              │      │   │
│  │  │   • compute_stability_score()              │      │   │
│  │  │   • get_recommendations()                  │      │   │
│  │  │   • full_analysis()                        │      │   │
│  │  └────────────────────────────────────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓ (Persist Data)                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Database Models (models.py)                 │   │
│  │  • Session (session metadata)                        │   │
│  │  • Reading (individual power values)                 │   │
│  │  • Analysis (full analysis results)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬────────────────────────────────────────────────┘
               ↓
        ┌──────────────┐
        │ powersense.db│  (SQLite)
        │              │
        │ - Sessions   │
        │ - Readings   │
        │ - Analysis   │
        └──────────────┘
```

---

## Component Details

### Frontend Layer (`templates/index.html`)
**Responsibility**: User Interface & Client-side Logic

**Pages**:
1. **Dashboard**
   - File upload (drag & drop)
   - Settings (tariff, wattage)
   - Analyze button
   - Results visualization
   - Export buttons

2. **History**
   - List all sessions
   - View/Delete options
   - Session metadata

3. **About**
   - Feature overview
   - Algorithm descriptions
   - Getting started guide

**Features**:
- Multi-page SPA (no page reloads)
- Real-time Chart.js visualizations
- Responsive design (mobile-friendly)
- Fetch API for backend communication
- Session state management

---

### Backend API Layer (`app.py`)
**Responsibility**: HTTP Endpoints & Request Handling

**Endpoints**:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Serve main HTML |
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload & analyze file |
| GET | `/api/history` | List all sessions |
| GET | `/api/session/<id>` | Get session details |
| GET | `/api/session/<id>` (DELETE) | Delete session |
| GET | `/api/export/<id>` | Export CSV/JSON |
| GET | `/api/recommendations/<id>` | Get insights |
| GET | `/api/forecast/<id>` | Get forecast |

**Request Flow**:
```
File Upload → Parse → Analyze → Store → Return Results
```

---

### ML/Analytics Layer (`ml_service.py`)
**Responsibility**: Data Analysis & Prediction

**PowerAnalyzer Class Methods**:

| Algorithm | Method | Purpose |
|-----------|--------|---------|
| Z-Score | `zscore_anomaly_detection()` | Detect outliers using std dev |
| Isolation Forest | `isolation_forest_detection()` | Robust ML-based anomaly detection |
| Fourier FFT | `fourier_analysis()` | Detect cyclic patterns |
| ARIMA | `arima_forecast()` | Time-series prediction |
| Linear Regression | `get_trend_analysis()` | Slope/trend detection |
| Markov Chain | `build_transition_matrix()` | State transition probabilities |
| Stability Score | `compute_stability_score()` | Health metric (0-100) |
| Recommendations | `get_recommendations()` | Actionable insights |

**Analysis Output**:
```json
{
  "global_stats": { ... },
  "zscore_anomalies": [ ... ],
  "isolation_forest_anomalies": [ ... ],
  "fourier_analysis": { ... },
  "trend_analysis": { ... },
  "forecast": { ... },
  "transition_matrix": { ... },
  "stability_score": 95.7,
  "cost_analysis": { ... },
  "recommendations": [ ... ]
}
```

---

### Data Layer (`models.py` + Database)
**Responsibility**: Persistent Storage

**Database Schema**:

```sql
-- Sessions
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    session_name TEXT,
    created_at DATETIME,
    file_name TEXT
);

-- Readings
CREATE TABLE readings (
    id INTEGER PRIMARY KEY,
    session_id INTEGER FOREIGN KEY,
    value FLOAT,
    timestamp TEXT,
    created_at DATETIME
);

-- Analysis Results
CREATE TABLE analysis (
    id INTEGER PRIMARY KEY,
    session_id INTEGER FOREIGN KEY,
    analysis_data JSON,  -- Full analysis stored as JSON
    created_at DATETIME
);
```

**Models**:
- `Session`: Represents one analysis session
- `Reading`: Individual power measurement
- `Analysis`: Complete analysis result set

---

## Data Flow Example

### Scenario: User uploads power log

```
1. User selects file in browser
   └─> JavaScript: handleDrop() / handleChange()
   └─> Show file name

2. User clicks "Analyse"
   └─> JavaScript: analyzeFile()
   └─> FormData with file + settings
   └─> POST /api/upload

3. Backend receives request
   └─> Flask: upload_and_analyze()
   └─> Parse file lines
   └─> Create Session in DB

4. Store readings
   └─> Create Reading rows (one per value)
   └─> Commit to DB

5. Run ML analysis
   └─> PowerAnalyzer.full_analysis()
   └─> Run 9 different algorithms
   └─> Compute recommendations

6. Store analysis
   └─> Create Analysis row with JSON data
   └─> Commit to DB

7. Return JSON response
   └─> Backend sends analysis + session_id
   └─> JavaScript receives response

8. Render results
   └─> populateStats()
   └─> renderLineChart()
   └─> renderDistChart()
   └─> renderForecastChart()
   └─> renderInsights()
   └─> Show export buttons

9. User exports results
   └─> POST /api/export/123?format=csv
   └─> Generate CSV from DB data
   └─> Browser downloads file
```

---

## Algorithm Pipeline

```
Raw Power Data
    ↓
[Statistical Analysis]
├─ Mean, Std Dev, Min, Max, Percentiles
├─ Normalization (Z-score)
└─ Distribution analysis

    ↓
[Anomaly Detection - Dual Method]
├─ Z-Score Based (threshold-based)
└─ Isolation Forest (ML-based)

    ↓
[Pattern Detection]
├─ Fourier Transform (cyclic patterns)
├─ Markov Chains (state transitions)
└─ Linear Regression (trend)

    ↓
[Forecasting]
├─ ARIMA (if available)
└─ Exponential Smoothing (fallback)

    ↓
[Scoring & Insights]
├─ Stability Score (0-100)
├─ Cost Analysis
└─ Recommendations

    ↓
Export-Ready Results
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **Visualization** | Chart.js | Real-time charts |
| **Backend** | Flask 2.3 | REST API framework |
| **ORM** | SQLAlchemy | Database abstraction |
| **Database** | SQLite | File-based storage |
| **ML/Analytics** | NumPy, SciPy, scikit-learn, statsmodels | Data science |
| **Server** | Python 3.8+ | Runtime |

---

## Scalability Considerations

### Current (Single Machine)
- SQLite database (suitable for ~10K sessions)
- Flask development server
- All data in-process

### Production Scaling
- **Database**: Replace SQLite with PostgreSQL
- **Server**: Use Gunicorn + Nginx
- **Async**: Add Celery for long-running analyses
- **Cache**: Add Redis for frequently accessed data
- **Monitoring**: Add logging, alerting, dashboards

---

## Security Notes

- CORS enabled for localhost only (modify in `app.py`)
- File upload validation included
- Database sanitization via SQLAlchemy ORM
- No authentication (add before production use)
- Max file size: 16MB

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Upload & Parse | <1s | Depends on file size |
| Z-Score Analysis | <100ms | O(n) complexity |
| Isolation Forest | 100-500ms | O(n log n) |
| Fourier Transform | 50-200ms | O(n log n) FFT |
| ARIMA (if available) | 500-2000ms | Model fitting |
| Full Analysis | 1-3s | All algorithms combined |
| Database Write | <500ms | ~300 readings |
| Export (CSV) | <500ms | File generation |

---

## Maintenance & Troubleshooting

### Common Issues

1. **"Port already in use"**
   - Change port in `app.py` line 337

2. **"Module not found"**
   - Run: `pip install -r requirements.txt`

3. **"Database locked"**
   - SQLite limitation; restart server

4. **"ARIMA not working"**
   - Falls back to exponential smoothing
   - Check: `from statsmodels...`

5. **"Memory high"**
   - Analyze smaller files
   - Clear old sessions in History

---

## Future Enhancements

1. ✅ Multi-algorithm anomaly detection
2. ✅ Time-series forecasting
3. ✅ Export to CSV/JSON
4. ⏳ WebSocket live streaming
5. ⏳ Authentication & multi-user
6. ⏳ Email reports
7. ⏳ Mobile app (React Native)
8. ⏳ Cloud deployment (AWS/GCP)
9. ⏳ Real-time notifications
10. ⏳ Comparative analysis (multi-session)

---

## Files & Responsibilities

```
webapp/
├── app.py                 # Flask app + API routes
├── models.py              # SQLAlchemy ORM models
├── ml_service.py          # PowerAnalyzer class
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Multi-page frontend
├── static/                # CSS/JS (optional)
├── sample_data.txt        # Test data
├── run.bat                # Windows startup
├── run.sh                 # Linux/Mac startup
├── README.md              # User guide
├── ARCHITECTURE.md        # This file
└── .gitignore             # Git ignore rules
```

---

## Contributing

To extend PowerSense:

1. **Add ML Algorithm**:
   - Edit `ml_service.py`
   - Add method to `PowerAnalyzer`
   - Call in `full_analysis()`

2. **Add API Endpoint**:
   - Edit `app.py`
   - Add `@app.route()` decorator
   - Connect to backend logic

3. **Update Frontend**:
   - Edit `templates/index.html`
   - Add page or section
   - Call API endpoint

4. **Database Schema Change**:
   - Edit `models.py`
   - Delete `powersense.db`
   - Restart (auto-creates new DB)

---

**PowerSense v2.0** - Intelligent Energy Analysis System Architecture
