from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension,
    MetricType,
)
from dotenv import load_dotenv
load_dotenv()

class GoogleAnalyticsConnector:
    """Handles connection and data fetching from Google Analytics 4."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the GA4 connector.
        
        Args:
            config: Configuration dictionary containing:
                - property_id: GA4 property ID
                - credentials: OAuth2 credentials dict
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validate_config(config)
        
        self.property_id = config['property_id']
        
        # Create credentials with all required fields
        self.credentials = Credentials(
            token=None,  # Token will be obtained through refresh
            refresh_token=config['credentials']['refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            client_id=config['credentials']['client_id'],
            client_secret=config['credentials']['client_secret'],
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)
        
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration."""
        required_keys = ['property_id', 'credentials']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        required_cred_keys = ['refresh_token', 'client_id', 'client_secret']
        missing_cred_keys = [
            key for key in required_cred_keys 
            if key not in config['credentials']
        ]
        if missing_cred_keys:
            raise ValueError(f"Missing required credential keys: {missing_cred_keys}")

    async def fetch_data(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        row_limit: int = 10000
    ) -> Dict[str, Any]:
        """
        Fetch data from GA4.
        
        Args:
            metrics: List of metric names to fetch
            dimensions: Optional list of dimension names
            start_date: Start date for the report (defaults to 30 days ago)
            end_date: End date for the report (defaults to today)
            row_limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing the fetched data
        """
        try:
            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Prepare dimensions
            dimension_list = []
            if dimensions:
                dimension_list = [Dimension(name=dim) for dim in dimensions]

            # Prepare metrics
            metric_list = [Metric(name=metric) for metric in metrics]

            # Create request
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=dimension_list,
                metrics=metric_list,
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d")
                    )
                ],
                limit=row_limit
            )

            # Execute request
            self.logger.info(
                f"Fetching GA4 data for date range: "
                f"{start_date.date()} to {end_date.date()}"
            )
            response = self.client.run_report(request)

            # Process response
            return self._process_response(response)

        except Exception as e:
            self.logger.error(f"Error fetching GA4 data: {str(e)}")
            raise

    def _process_response(self, response: Any) -> Dict[str, Any]:
        """
        Process the GA4 API response into a structured format.
        
        Args:
            response: Raw GA4 API response
            
        Returns:
            Processed data dictionary
        """
        try:
            # Extract dimension headers
            dimension_headers = [
                header.name for header in response.dimension_headers
            ]

            # Extract metric headers
            metric_headers = [
                {
                    'name': header.name,
                    'type': MetricType(header.type_).name
                }
                for header in response.metric_headers
            ]

            # Process rows
            rows = []
            for row in response.rows:
                # Process dimensions
                dimension_values = [
                    value.value for value in row.dimension_values
                ]
                
                # Process metrics
                metric_values = [
                    value.value for value in row.metric_values
                ]
                
                # Combine into row dict
                row_dict = {}
                
                # Add dimensions
                for header, value in zip(dimension_headers, dimension_values):
                    row_dict[header] = value
                    
                # Add metrics
                for header, value in zip(metric_headers, metric_values):
                    row_dict[header['name']] = self._convert_metric_value(
                        value,
                        header['type']
                    )
                    
                rows.append(row_dict)

            return {
                'dimension_headers': dimension_headers,
                'metric_headers': metric_headers,
                'rows': rows,
                'row_count': len(rows),
                'totals': self._process_totals(response),
                'metadata': {
                    'property_id': self.property_id
                }
            }

        except Exception as e:
            self.logger.error(f"Error processing GA4 response: {str(e)}")
            raise

    def _process_totals(self, response: Any) -> Dict[str, Any]:
        """
        Process the totals from the GA4 response.
        
        Args:
            response: GA4 API response
            
        Returns:
            Dictionary of total values
        """
        totals = {}
        
        if response.totals:
            for i, header in enumerate(response.metric_headers):
                totals[header.name] = self._convert_metric_value(
                    response.totals[0].metric_values[i].value,
                    MetricType(header.type_).name
                )
                
        return totals

    def _convert_metric_value(self, value: str, metric_type: str) -> Any:
        """
        Convert metric value to appropriate type.
        
        Args:
            value: String value from GA4
            metric_type: MetricType name
            
        Returns:
            Converted value
        """
        try:
            if metric_type == 'TYPE_INTEGER':
                return int(value)
            elif metric_type == 'TYPE_FLOAT':
                return float(value)
            elif metric_type == 'TYPE_CURRENCY':
                return float(value)
            else:
                return value
        except (ValueError, TypeError):
            self.logger.warning(
                f"Could not convert value '{value}' to type {metric_type}"
            )
            return value

    async def validate_credentials(self) -> bool:
        """
        Validate the credentials by making a test request.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            # Make a minimal request to test credentials
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                metrics=[Metric(name="activeUsers")],
                date_ranges=[
                    DateRange(
                        start_date="yesterday",
                        end_date="today"
                    )
                ]
            )
            
            self.client.run_report(request)
            return True
            
        except Exception as e:
            self.logger.error(f"Credential validation failed: {str(e)}")
            return False
