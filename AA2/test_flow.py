import asyncio
from src.flows.report_generation_flow import graph
from src.models.report_models import ReportStateInput
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_flow():
    try:
        # Test input data
        input_data = {
            "property_id": "123456789",  # GA4 property ID
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "metrics": ["totalUsers", "newUsers"],
            "dimensions": ["date", "deviceCategory"]
        }
        
        logger.info("Starting flow test with input: %s", input_data)
        
        # Create input state
        state_input = ReportStateInput(**input_data)
        
        # Run flow
        logger.info("Invoking graph...")
        result = await graph.ainvoke(state_input)
        
        logger.info("Flow completed successfully")
        logger.info("Result: %s", result)
        
        return result
        
    except Exception as e:
        logger.error("Error running flow: %s", str(e), exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(test_flow())
