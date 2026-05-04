# PowerSense - Quick Start Guide

## 🚀 Get Running in 3 Minutes

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server (30 seconds)

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
bash run.sh
```

Or manually:
```bash
python app.py
```

### Step 3: Open in Browser (30 seconds)
```
http://localhost:5000
```

---

## 📊 Test with Sample Data

1. Click on Dashboard
2. Upload the included `sample_data.txt`
3. Click "Analyse"
4. View results:
   - Charts with readings
   - Stability score
   - 10-step forecast
   - Cost estimates
   - Recommendations

---

## 💾 View Your Analyses

1. Click on "History"
2. See all past sessions
3. Click "View" to re-examine results
4. Click "Delete" to remove

---

## 📥 Export Results

After analysis, export as:
- **CSV** - Spreadsheet format
- **JSON** - For data science tools

---

## 🤖 What's Analyzed

Every upload runs **9 algorithms**:

1. ✅ Z-Score Anomaly Detection
2. ✅ Isolation Forest (ML anomalies)
3. ✅ Fourier Analysis (patterns)
4. ✅ ARIMA Forecasting (predictions)
5. ✅ Trend Analysis
6. ✅ Markov Chains (transitions)
7. ✅ Stability Scoring
8. ✅ Cost Analysis
9. ✅ Smart Recommendations

---

## ⚙️ Settings

**Electricity Tariff** (₦/kWh)
- Default: 68
- Adjust for your provider

**Appliance Wattage** (Watts)
- Optional (auto-detects if 0)
- Use if you know exact wattage

---

## 📝 Your Data Format

Plain text, one value per line:

**Simple:**
```
2.48
2.49
2.50
```

**With Timestamps:**
```
10:30:15 2.48
10:30:16 2.49
10:30:17 2.50
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Edit `app.py` change port to 5001 |
| Module not found | `pip install -r requirements.txt` |
| No results | Check file format (one value per line) |
| Crash on startup | Delete `powersense.db` and restart |

---

## 📚 Learn More

- **README.md** - Full documentation
- **ARCHITECTURE.md** - System design
- **sample_data.txt** - Test data

---

## 🎯 Common Tasks

### Run analysis on your own data
1. Export power readings to `.txt`
2. Upload to dashboard
3. Set tariff (₦68 default)
4. Click Analyse

### Compare multiple sessions
1. Upload session 1
2. View & export results
3. Upload session 2
4. Check History page

### Export for reports
1. Analyze data
2. Click "Export CSV" or "Export JSON"
3. Use in Excel, Python, or other tools

---

## ✨ Key Features

🔴 **Live Anomaly Detection** - Spikes highlighted in red  
📈 **10-Step Forecast** - Predict next readings  
💰 **Cost Breakdown** - Daily/monthly estimates  
⭐ **Stability Score** - System health (0-100)  
📊 **Distribution Chart** - See value spread  
💡 **Smart Recommendations** - Actionable insights  
📥 **Full Export** - CSV or JSON format  

---

## 🆘 Need Help?

1. Check browser console (F12)
2. Check terminal where server runs
3. Verify file format is correct
4. Try sample_data.txt first

---

**PowerSense Ready!** 🎉  
Start analyzing power usage now →  http://localhost:5000
