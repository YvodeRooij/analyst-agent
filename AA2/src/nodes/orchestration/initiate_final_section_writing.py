import logging
from typing import Dict, List
from langgraph.prebuilt import ToolMessage
from src.models.report_models import ReportState

logger = logging.getLogger(__name__)

def initiate_final_section_writing(state: ReportState, config: Dict) -> List[ToolMessage]:
    """
    Initiate parallel writing of final sections (executive summary and recommendations)
    
    Args:
        state: Current state containing sections to write
        config: Configuration dictionary
        
    Returns:
        List of Send objects for parallel section writing
    """
    try:
        logger.info("Initiating final section writing")
        
        # Get sections that don't require analysis (summary and recommendations)
        sections = state.get("sections", [])
        final_sections = [s for s in sections if not s.research]
        
        logger.info(f"Found {len(final_sections)} final sections to write")
        
        # Create Send objects for parallel processing
        sends = []
        for section in final_sections:
            sends.append(
                ToolMessage(
                    tool="write_final_sections",
                    args={
                        "section": section,
                        "state": state,
                        "config": config
                    }
                )
            )
            
        return sends
        
    except Exception as e:
        logger.error(f"Error initiating final section writing: {str(e)}", exc_info=True)
        raise
