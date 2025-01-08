import logging
from typing import Dict
from src.models.report_models import ReportState, SectionState
from src.utils.source_formatting import format_sections

logger = logging.getLogger(__name__)

def gather_completed_sections(state: ReportState, config: Dict) -> ReportState:
    """
    Gather and format all completed GA4 analysis sections
    
    Args:
        state: Current state containing completed sections
        config: Configuration dictionary
        
    Returns:
        Updated state with formatted sections
    """
    try:
        logger.info("Gathering completed GA4 analysis sections")
        
        # Get sections from state
        sections = state.get("sections", [])
        
        if not sections:
            logger.warning("No sections found in state")
            return state
            
        # Filter out sections without content
        completed_sections = [s for s in sections if s.content]
        
        if not completed_sections:
            logger.warning("No completed sections found")
            return state
            
        # Add completed sections back to state
        state["sections"] = completed_sections
        
        logger.info(f"Successfully gathered {len(completed_sections)} sections")
        return state
        
    except Exception as e:
        logger.error(f"Error gathering completed sections: {str(e)}", exc_info=True)
        raise
