import logging
from typing import Dict, List
from langchain_openai import ChatOpenAI
from src.models.report_models import Section, SectionState
from src.prompts.writing_prompts import section_writer_instructions

logger = logging.getLogger(__name__)

def write_section(state: Dict, config: Dict) -> Dict:
    """
    Write content for a section using GA4 data analysis
    
    Args:
        section: Section to write content for
        state: Current state containing GA4 data and other context
        config: Configuration dictionary
        
    Returns:
        List containing the updated section
    """
    try:
        logger.info("Starting section writing process")
        
        # Get data from state
        ga_data = state.get("ga_data", {})
        llm_config = config.get("llm_config", {})
        analysis = state.get("analysis", "")
        insights = state.get("insights", "")
        sections = state.get("sections", [])
        
        # Get sections that need writing
        research_sections = [s for s in sections if s.research and not s.content]
        
        if not research_sections:
            logger.info("No sections to write")
            return state
            
        # Process each section
        for section in research_sections:
            # Extract metrics, dimensions, and growth data
            metric_headers = [h.get('name') for h in ga_data.get('metric_headers', [])]
            dimension_headers = ga_data.get('dimension_headers', [])
            totals = ga_data.get('totals', {})
            growth_metrics = ga_data.get('growth_metrics', {})
            
            # Get relevant rows and prepare growth insights
            section_lower = section.name.lower()
            rows = ga_data.get('rows', [])[:10]
            
            # Format growth metrics with clear comparisons
            growth_insights = []
            for metric in metric_headers:
                if metric in growth_metrics:
                    growth_data = growth_metrics[metric]
                    current_val = growth_data['current']
                    growth_rate = growth_data['growth_rate']
                    
                    # Format metric name for display
                    metric_display = metric.replace('total', '').replace('average', 'avg')
                    
                    # Create growth insight with MoM comparison
                    if abs(growth_rate) > 1:  # Only show significant changes
                        direction = "increase" if growth_rate > 0 else "decrease"
                        insight = f"{metric_display}: {current_val:.1f} ({abs(growth_rate):.1f}% {direction} MoM)"
                        growth_insights.append(insight)
            
            # Prepare section-specific metrics with growth data
            section_metrics = {
                'totals': totals,
                'relevant_rows': rows,
                'key_metrics': [m for m in metric_headers if _is_relevant_metric(m, section_lower)],
                'key_dimensions': [d for d in dimension_headers if _is_relevant_dimension(d, section_lower)],
                'growth_insights': growth_insights
            }
            
            # Prepare writing prompt with growth focus
            writing_prompt = f"""Write a detailed {section.name} section for the GA4 analytics report.

Section Requirements:
{section.description}

Overall Analysis Context:
{analysis}

Key Growth Insights:
{chr(10).join(growth_insights)}

Key Insights:
{insights}

Section-Specific Metrics:
Total Values: {section_metrics['totals']}
Key Metrics to Focus On: {section_metrics['key_metrics']}
Key Dimensions to Consider: {section_metrics['key_dimensions']}

Sample Data Points:
{section_metrics['relevant_rows']}

Write a concise and worldclass analysis that:
1. Addresses the section requirements
2. Incorporates relevant metrics and dimensions
3. Provides actionable insights
4. Uses specific data points to support conclusions
"""
            
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=llm_config.get("temperature", 0.7)
            )
            
            # Generate content
            response = llm.invoke(writing_prompt)
            section.content = response.content
            
            print(f"Section content: {vars(section)}")
            logger.info(f"Completed writing section: {section.name}")
        
        # Update state with written sections
        state["sections"] = sections
        return state
        
    except Exception as e:
        logger.error(f"Error writing section: {str(e)}", exc_info=True)
        raise

def _is_relevant_metric(metric: str, section_type: str) -> bool:
    """Helper function to determine if a metric is relevant for a section"""
    metric = metric.lower()
    
    if "executive" in section_type or "overview" in section_type:
        return True  # All metrics relevant for executive summary
        
    if "performance" in section_type:
        return any(x in metric for x in ["users", "sessions", "views", "rate"])
        
    if "behavior" in section_type:
        return any(x in metric for x in ["session", "engagement", "duration", "views"])
        
    if "recommendation" in section_type:
        return True  # All metrics potentially relevant for recommendations
        
    return False

def _is_relevant_dimension(dimension: str, section_type: str) -> bool:
    """Helper function to determine if a dimension is relevant for a section"""
    dimension = dimension.lower()
    
    if "executive" in section_type or "overview" in section_type:
        return True  # All dimensions relevant for executive summary
        
    if "performance" in section_type:
        return any(x in dimension for x in ["source", "medium", "campaign", "channel"])
        
    if "behavior" in section_type:
        return any(x in dimension for x in ["page", "device", "country"])
        
    if "recommendation" in section_type:
        return True  # All dimensions potentially relevant for recommendations
        
    return False
