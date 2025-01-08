import logging
import yaml
import os
from datetime import datetime, timedelta
from typing import Dict
from src.connectors.google_analytics import GoogleAnalyticsConnector
from src.models.report_models import ReportState

logger = logging.getLogger(__name__)

async def fetch_ga_data(state: ReportState, config: Dict) -> ReportState:
    """
    Fetch data from Google Analytics 4 using the GoogleAnalyticsConnector.
    
    Args:
        state: Current state of the report generation
        config: Configuration dictionary containing GA settings
        
    Returns:
        Updated state with GA data
    """
    try:
        logger.info("Initializing GA4 data fetch")
        
        # Load GA config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config", "config.yaml")
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f)
            ga_config = yaml_config.get("ga_config", {})
        
        # Initialize GA connector with configuration
        ga_connector = GoogleAnalyticsConnector({
            'property_id': state.get('property_id'),
            'credentials': {
                'refresh_token': os.getenv('GA_REFRESH_TOKEN'),
                'client_id': os.getenv('GA_CLIENT_ID'),
                'client_secret': os.getenv('GA_CLIENT_SECRET')
            }
        })
        
        # Validate credentials
        if not await ga_connector.validate_credentials():
            raise ValueError("Failed to validate GA4 credentials")
        
        # Calculate date ranges for weekly and monthly comparisons
        end_date = datetime.now()
        # Weekly ranges
        start_date = end_date - timedelta(days=7)  # Last 7 days
        prev_week_start = start_date - timedelta(days=7)  # Previous week
        
        # Monthly ranges
        current_month_start = end_date.replace(day=1)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # Fetch current week data
        current_data = await ga_connector.fetch_data(
            metrics=ga_config.get("metrics", []),
            dimensions=ga_config.get("dimensions", []),
            start_date=start_date,
            end_date=end_date,
            row_limit=ga_config.get("row_limit", 10000)
        )
        
        # Fetch previous week data
        previous_week_data = await ga_connector.fetch_data(
            metrics=ga_config.get("metrics", []),
            dimensions=ga_config.get("dimensions", []),
            start_date=prev_week_start,
            end_date=start_date,
            row_limit=ga_config.get("row_limit", 10000)
        )
        
        # Fetch current month data
        current_month_data = await ga_connector.fetch_data(
            metrics=ga_config.get("metrics", []),
            dimensions=ga_config.get("dimensions", []),
            start_date=current_month_start,
            end_date=end_date,
            row_limit=ga_config.get("row_limit", 10000)
        )
        
        # Fetch previous month data
        previous_month_data = await ga_connector.fetch_data(
            metrics=ga_config.get("metrics", []),
            dimensions=ga_config.get("dimensions", []),
            start_date=last_month_start,
            end_date=last_month_end,
            row_limit=ga_config.get("row_limit", 10000)
        )
        
        # Calculate weekly and monthly growth rates
        growth_metrics = {
            'weekly': {},
            'monthly': {}
        }
        
        for metric in current_data.get('metric_headers', []):
            metric_name = metric.get('name')
            
            # Weekly comparisons
            current_week_value = float(current_data.get('totals', {}).get(metric_name, 0))
            prev_week_value = float(previous_week_data.get('totals', {}).get(metric_name, 0))
            
            if prev_week_value > 0:
                weekly_growth = ((current_week_value - prev_week_value) / prev_week_value) * 100
                growth_metrics['weekly'][metric_name] = {
                    'current': current_week_value,
                    'previous': prev_week_value,
                    'growth_rate': round(weekly_growth, 2)
                }
            
            # Monthly comparisons
            current_month_value = float(current_month_data.get('totals', {}).get(metric_name, 0))
            prev_month_value = float(previous_month_data.get('totals', {}).get(metric_name, 0))
            
            if prev_month_value > 0:
                monthly_growth = ((current_month_value - prev_month_value) / prev_month_value) * 100
                growth_metrics['monthly'][metric_name] = {
                    'current': current_month_value,
                    'previous': prev_month_value,
                    'growth_rate': round(monthly_growth, 2)
                }
        
        # Combine all data
        ga_data = {
            'current_week': current_data,
            'previous_week': previous_week_data,
            'current_month': current_month_data,
            'previous_month': previous_month_data,
            'growth_metrics': growth_metrics,
            'time_ranges': {
                'weekly': {
                    'current': {'start': start_date.date(), 'end': end_date.date()},
                    'previous': {'start': prev_week_start.date(), 'end': start_date.date()}
                },
                'monthly': {
                    'current': {'start': current_month_start.date(), 'end': end_date.date()},
                    'previous': {'start': last_month_start.date(), 'end': last_month_end.date()}
                }
            }
        }
        
        logger.info(
            f"Successfully fetched GA data:\n"
            f"- Time Range: {start_date.date()} to {end_date.date()}\n"
            f"- Rows: {ga_data.get('row_count', 0)}\n"
            f"- Metrics: {len(ga_data.get('metric_headers', []))}\n"
            f"- Dimensions: {len(ga_data.get('dimension_headers', []))}"
        )
        
        # Add GA data to state
        state["ga_data"] = ga_data
        
        return state
        
    except Exception as e:
        logger.error(f"Error fetching GA data: {str(e)}", exc_info=True)
        # Add error info to state
        state["ga_data"] = {
            "error": str(e),
            "rows": [],
            "row_count": 0,
            "dimension_headers": [],
            "metric_headers": [],
            "totals": {},
            "metadata": {
                "property_id": state.get('property_id')
            }
        }
        return state
