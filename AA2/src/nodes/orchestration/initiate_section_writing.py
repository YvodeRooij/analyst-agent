import logging
from typing import Dict, List
from langgraph.prebuilt import ToolMessage
from src.models.report_models import ReportState

logger = logging.getLogger(__name__)

def initiate_section_writing(state: ReportState, config: Dict) -> List[ToolMessage]:
    """
    Initiate parallel writing of GA4 analysis sections
    
    Args:
        state: Current state containing sections to write
        config: Configuration dictionary
        
    Returns:
        List of Send objects for parallel section writing
    """
    try:
        logger.info("Initiating GA4 analysis section writing")
        
        # Get sections that require analysis
        sections = state.get("sections", [])
        analysis_sections = [s for s in sections if s.research]
        
        logger.info(f"Found {len(analysis_sections)} sections requiring analysis")
        
        # Create Send objects for parallel processing
        sends = []
        for section in analysis_sections:
            sends.append(
                ToolMessage(
                    tool="write_section",
                    args={
                        "section": section,
                        "state": state,
                        "config": config
                    }
                )
            )
            
        return sends
        
    except Exception as e:
        logger.error(f"Error initiating section writing: {str(e)}", exc_info=True)
        raise
