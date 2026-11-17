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

# Extended agents (already present in project)
try:
    from agents.warehouse_agent import WarehouseAgent
    from agents.sourcing_agent import SourcingAgent
    from agents.pricing_agent import PricingAgent
    from agents.returns_agent import ReturnsAgent
    from agents.compliance_agent import ComplianceAgent
    from agents.geography_agent import GeographyAgent
    from agents.capacity_agent import CapacityAgent
    from agents.carbon_agent import CarbonAgent
    from agents.forecast_bias_agent import ForecastBiasAgent
    from agents.segment_agent import SegmentAgent
    _EXTENDED = [
        WarehouseAgent, SourcingAgent, PricingAgent, ReturnsAgent,
        ComplianceAgent, GeographyAgent, CapacityAgent, CarbonAgent,
        ForecastBiasAgent, SegmentAgent,
    ]
except ImportError:
    _EXTENDED = []

# Brand-new agents added in this enhancement
from agents.correlation_agent import CorrelationAgent
from agents.trend_agent import TrendAgent
from agents.reorder_agent import ReorderAgent
from agents.distribution_agent import DistributionAgent

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
] + _EXTENDED + [
    CorrelationAgent,
    TrendAgent,
    ReorderAgent,
    DistributionAgent,
]
