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
        
        # Calculate date ranges for current and previous periods
        end_date = datetime.now()
        start_date = end_date - timedelta(days=ga_config.get("default_days", 30))
        prev_start_date = start_date - timedelta(days=ga_config.get("default_days", 30))
        
        # Fetch current period data
        current_data = await ga_connector.fetch_data(
            metrics=ga_config.get("metrics", []),
            dimensions=ga_config.get("dimensions", []),
            start_date=start_date,
            end_date=end_date,
            row_limit=ga_config.get("row_limit", 10000)
        )
        
        # Fetch previous period data
        previous_data = await ga_connector.fetch_data(
            metrics=ga_config.get("metrics", []),
            dimensions=ga_config.get("dimensions", []),
            start_date=prev_start_date,
            end_date=start_date,
            row_limit=ga_config.get("row_limit", 10000)
        )
        
        # Calculate growth rates and trends
        growth_metrics = {}
        for metric in current_data.get('metric_headers', []):
            metric_name = metric.get('name')
            current_value = float(current_data.get('totals', {}).get(metric_name, 0))
            prev_value = float(previous_data.get('totals', {}).get(metric_name, 0))
            
            if prev_value > 0:
                growth_rate = ((current_value - prev_value) / prev_value) * 100
                growth_metrics[metric_name] = {
                    'current': current_value,
                    'previous': prev_value,
                    'growth_rate': round(growth_rate, 2)
                }
        
        # Combine data
        ga_data = {
            **current_data,
            'previous_period': previous_data,
            'growth_metrics': growth_metrics
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
