"""
Configuration for PowerSense
"""

import os

# Database
DATABASE_PATH = 'powersense.db'
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask
DEBUG = True
HOST = 'localhost'
PORT = 5000
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Analysis Parameters
DEFAULT_TARIFF = 68  # Naira per kWh
DEFAULT_WATTAGE = 0  # Auto-detect
ML_FORECAST_PERIODS = 10  # Steps ahead to predict
ANOMALY_CONTAMINATION = 0.1  # Isolation Forest contamination

# CORS
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://127.0.0.1:5000']

# Logging
LOG_LEVEL = 'INFO'
