import os
import asyncio
import logging
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from src.flows.report_generation_flow import graph
from src.models.report_models import ReportStateInput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Load environment variables
        load_dotenv()

        # Validate required environment variables
        required_vars = [
            'OPENAI_API_KEY',
            'GA_PROPERTY_ID',
            'GA_CLIENT_ID',
            'GA_CLIENT_SECRET',
            'GA_REFRESH_TOKEN'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Define input state
        input_state = ReportStateInput(property_id=os.getenv('GA_PROPERTY_ID'))

        # Execute the graph
        result = await graph.ainvoke(input_state)
        
        if isinstance(result, dict) and 'final_report' in result:
            logger.info("Final report generated successfully")
            print("\nFinal Report:")
            print("-------------")
            print(result['final_report'])
        else:
            logger.warning("No final report generated in output")
            logger.debug(f"Output type: {type(result)}, content: {result}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
