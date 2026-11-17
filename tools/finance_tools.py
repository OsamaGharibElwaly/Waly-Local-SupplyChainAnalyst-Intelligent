"""Financial helpers: margins, EOQ, safety stock, ROP, inventory turnover."""
import math


def gross_margin(revenue, cost):
    if revenue is None or revenue <= 0:
        return None
    return round((revenue - cost) / revenue, 4)


def eoq(annual_demand, order_cost, holding_cost_per_unit):
    if not annual_demand or not order_cost or not holding_cost_per_unit:
        return None
    if annual_demand <= 0 or order_cost <= 0 or holding_cost_per_unit <= 0:
        return None
    return round(math.sqrt(2 * annual_demand * order_cost / holding_cost_per_unit), 2)


def safety_stock(z_score, demand_std, lead_time_days):
    if z_score is None or demand_std is None or lead_time_days is None:
        return None
    if lead_time_days <= 0:
        return None
    return round(z_score * demand_std * math.sqrt(lead_time_days), 2)


def reorder_point(avg_daily_demand, lead_time_days, safety_stock_value=0):
    if avg_daily_demand is None or lead_time_days is None:
        return None
    return round(avg_daily_demand * lead_time_days + (safety_stock_value or 0), 2)


def inventory_turnover(cogs, avg_inventory):
    if not avg_inventory or avg_inventory <= 0:
        return None
    return round(cogs / avg_inventory, 2)


def days_of_inventory(avg_inventory, cogs, days=365):
    if not cogs or cogs <= 0:
        return None
    return round(avg_inventory / (cogs / days), 1)
