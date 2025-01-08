import logging
from typing import List
from src.models.report_models import Section

logger = logging.getLogger(__name__)

def format_sections(sections: List[Section]) -> str:
    """
    Format a list of sections into a readable string
    
    Args:
        sections: List of Section objects
        
    Returns:
        Formatted string containing section information
    """
    try:
        formatted_sections = []
        
        for section in sections:
            section_info = [
                f"\nSECTION: {section.name}",
                f"DESCRIPTION: {section.description}",
                f"REQUIRES ANALYSIS: {'Yes' if section.research else 'No'}"
            ]
            
            if section.content:
                section_info.append("CONTENT:")
                section_info.append(section.content)
                
            section_info.append("---")
            formatted_sections.append('\n'.join(section_info))
            
        return '\n'.join(formatted_sections)
        
    except Exception as e:
        logger.error(f"Error formatting sections: {str(e)}", exc_info=True)
        return "Error occurred while formatting sections."
