import logging
from typing import Dict
from langchain_openai import ChatOpenAI
from src.models.report_models import ReportState, Section
from src.prompts.planning_prompts import report_planner_instructions

logger = logging.getLogger(__name__)

def generate_report_plan(state: ReportState, config: Dict) -> ReportState:
    """
    Generate a report plan based on GA4 data analysis
    
    Args:
        state: Current report state containing GA4 data
        config: Configuration dictionary
        
    Returns:
        Updated state with planned sections
    """
    try:
        logger.info("Generating report plan based on GA4 data")
        
        # Get GA data and config
        ga_data = state.get("ga_data", {})
        llm_config = config.get("llm_config", {})
        
        # Extract key metrics and dimensions
        metric_headers = [h.get('name') for h in ga_data.get('metric_headers', [])]
        dimension_headers = ga_data.get('dimension_headers', [])
        totals = ga_data.get('totals', {})
        
        # Get analysis and insights
        analysis = state.get("analysis", "")
        insights = state.get("insights", "")
        
        # Prepare planning prompt
        planning_prompt = f"""Based on the GA4 data analysis and insights, create a detailed analytics report plan.

Available GA4 Data:
Metrics: {metric_headers}
Dimensions: {dimension_headers}
Overall Metrics: {totals}

Analysis Summary:
{analysis}

Key Insights:
{insights}

Create a report plan with the following sections:
1. Executive Summary (high-level overview)
2. Key Performance Metrics (detailed metrics analysis)
3. User Behavior Analysis (patterns and trends)
4. Recommendations (actionable insights)

For each section, provide:
- Clear section name
- Detailed description of what to include
- Specific metrics and dimensions to focus on
"""
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=llm_config.get("temperature", 0.7)
        )
        
        # Generate plan
        response = llm.invoke(planning_prompt)
        plan = response.content
        
        # Parse sections from plan
        sections = []
        current_section = None
        
        for line in plan.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#') or line.endswith(':'):
                # New section
                if current_section:
                    sections.append(current_section)
                    
                name = line.lstrip('#').strip().rstrip(':')
                current_section = Section(
                    name=name,
                    description="",
                    research=True  # Default to True for analysis sections
                )
                
            elif current_section:
                # Add to current section description
                current_section.description += line + "\n"
                
                # Check if this line indicates research requirement
                lower_line = line.lower()
                if "executive summary" in lower_line or "recommendation" in lower_line:
                    current_section.research = False
        
        # Add final section
        if current_section:
            sections.append(current_section)
            
        # Update state
        state["sections"] = sections
        logger.info(f"Generated plan with {len(sections)} sections")
        
        return state
        
    except Exception as e:
        logger.error(f"Error generating report plan: {str(e)}", exc_info=True)
        raise
