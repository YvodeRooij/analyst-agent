import logging
from typing import Dict, List
from langchain_openai import ChatOpenAI
from src.models.report_models import Section, SectionState
from src.prompts.writing_prompts import final_section_writer_instructions
from src.utils.source_formatting import format_sections

logger = logging.getLogger(__name__)

def write_final_sections(state: Dict, config: Dict) -> Dict:
    """
    Write final sections (executive summary or recommendations) using GA4 data and analysis
    
    Args:
        state: Current state containing GA4 data and analysis
        config: Configuration dictionary
        
    Returns:
        Updated state with written final sections
    """
    try:
        logger.info("Starting final sections writing process")
        
        # Get data from state
        ga_data = state.get("ga_data", {})
        sections = state.get("sections", [])
        llm_config = config.get("llm_config", {})
        analysis = state.get("analysis", "")
        insights = state.get("insights", "")
        
        # Get final sections
        final_sections = [s for s in sections if not s.research]
        
        if not final_sections:
            logger.info("No final sections to write")
            return state
            
        # Process each final section
        for section in final_sections:
            # Extract key metrics and dimensions
            metric_headers = [h.get('name') for h in ga_data.get('metric_headers', [])]
            dimension_headers = ga_data.get('dimension_headers', [])
            totals = ga_data.get('totals', {})
            
            # Get completed analysis sections for context
            completed_sections = [s for s in sections if s.research and s.content]
            analysis_context = "\n\n".join([f"{s.name}:\n{s.content}" for s in completed_sections])
            
            # Prepare writing prompt
            writing_prompt = f"""Write a detailed {section.name} for the GA4 analytics report.

Section Requirements:
{section.description}

Overall Analysis:
{analysis}

Key Insights:
{insights}

Previous Analysis Sections:
{analysis_context}

Key Metrics Overview:
Total Values: {totals}
Available Metrics: {metric_headers}
Available Dimensions: {dimension_headers}

Write a comprehensive {"executive summary" if "summary" in section.name.lower() else "recommendations section"} that:
1. Synthesizes the key findings and insights
2. Highlights the most important metrics and trends
3. {"Provides a high-level overview of performance" if "summary" in section.name.lower() else "Offers specific, actionable recommendations"}
4. Uses data points to support conclusions
"""
            
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=llm_config.get("temperature", 0.7)
            )
            
            # Generate content
            response = llm.invoke(writing_prompt)
            section.content = response.content
            
            logger.info(f"Completed writing final section: {section.name}")
        
        # Update state with written sections
        state["sections"] = sections
        return state
        
    except Exception as e:
        logger.error(f"Error writing final section: {str(e)}", exc_info=True)
        raise
