from agents.demand_forecast import DemandForecastAgent
from agents.inventory_agent import InventoryAgent
from agents.supplier_agent import SupplierAgent
from agents.logistics_agent import LogisticsAgent
from agents.risk_agent import RiskAgent
from agents.sentiment_agent import SentimentAgent
from agents.cost_agent import CostAgent
from agents.quality_agent import QualityAgent
from agents.leadtime_agent import LeadTimeAgent
from agents.anomaly_agent import AnomalyAgent

ALL_AGENTS = [
    DemandForecastAgent,
    InventoryAgent,
    SupplierAgent,
    LogisticsAgent,
    RiskAgent,
    SentimentAgent,
    CostAgent,
    QualityAgent,
    LeadTimeAgent,
    AnomalyAgent,
]
