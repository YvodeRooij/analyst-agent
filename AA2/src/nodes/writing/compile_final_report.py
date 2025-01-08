import logging
from typing import Dict
from src.models.report_models import ReportState
from src.utils.email_sender import send_email

logger = logging.getLogger(__name__)

def compile_final_report(state: ReportState, config: Dict) -> ReportState:
    """
    Compile the final analytics report by combining all GA4 analysis sections.
    
    Args:
        state: Current state containing GA4 data and analysis sections
        config: Configuration dictionary
        
    Returns:
        Updated state with final report
    """
    try:
        logger.info("Compiling final analytics report")
        
        # Get GA data metadata
        ga_data = state.get("ga_data", {})
        metric_headers = [h.get('name') for h in ga_data.get('metric_headers', [])]
        dimension_headers = ga_data.get('dimension_headers', [])
        totals = ga_data.get('totals', {})
        
        # Get sections
        sections = state.get("sections", [])
        if not sections:
            logger.warning("No sections found to compile")
            state["final_report"] = "No sections available to compile report."
            return state
            
        # Format final report in markdown
        final_report = f"""
# GOOGLE ANALYTICS 4 PERFORMANCE REPORT

## OVERVIEW

**Property ID:** {ga_data.get('metadata', {}).get('property_id', 'Not specified')}  
**Total Rows Analyzed:** {ga_data.get('row_count', 0)}

<div class="metrics">

### Overall Metrics
{totals}

</div>

"""
        
        # Add each section's content in order
        for section in sections:
            if section.content:
                # Remove any existing section numbering if present
                section_name = section.name.strip('0123456789. ')
                final_report += f"\n{section.content}\n"
                
        logger.info(f"Successfully compiled report with {len(sections)} sections")
        
        # Update state with final report
        state["final_report"] = final_report
        
        # Send email with report
        logger.info("Sending report via email")
        subject = "Google Analytics 4 Performance Report"
        send_email(subject, final_report)
        
        logger.info("Successfully compiled and sent final report")
        return state
        
    except Exception as e:
        logger.error(f"Error compiling final report: {str(e)}", exc_info=True)
        raise
