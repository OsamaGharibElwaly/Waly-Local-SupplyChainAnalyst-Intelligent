"""Global configuration for Supply Chain Analyst."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

APP_NAME = "Supply Chain Analyst (Agentic Local AI)"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Thresholds used by rule-based agents
THRESHOLDS = {
    "low_stock_days": 15,
    "high_lead_time": 30,
    "high_defect_rate": 0.03,
    "supplier_score_warn": 60,
    "anomaly_zscore": 2.5,
    "sentiment_negative": -0.15,
}
