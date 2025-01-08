import logging
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from typing import Dict, List
from typing import TypedDict, Sequence
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from src.models.report_models import ReportState, ReportStateInput, ReportStateOutput, Section, SectionState, SectionOutputState
from src.nodes.data_fetching.fetch_ga_data import fetch_ga_data
from src.nodes.planning.generate_report_plan import generate_report_plan
from src.nodes.writing.write_section import write_section
from src.nodes.writing.write_final_sections import write_final_sections
from src.nodes.writing.gather_completed_sections import gather_completed_sections
from src.nodes.writing.compile_final_report import compile_final_report
from src.prompts.writing_prompts import section_writer_instructions, final_section_writer_instructions

logger = logging.getLogger(__name__)

# Initialize global tracer and callback manager
tracer = LangChainTracer(project_name="ga4-analytics-report")
callback_manager = CallbackManager([tracer])

def analyze_ga_data(state: ReportState, config: Dict) -> ReportState:
    """Analyze GA4 data to identify key patterns and trends"""
    try:
        logger.info("Analyzing GA4 data")
        
        # Get GA data and config
        ga_data = state.get("ga_data", {})
        llm_config = config.get("llm_config", {})
        
        # Initialize LLM with callback manager
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=llm_config.get("temperature", 0.7),
            callbacks=callback_manager.handlers
        )
        
        # Extract weekly and monthly metrics
        weekly_metrics = ga_data.get('growth_metrics', {}).get('weekly', {})
        monthly_metrics = ga_data.get('growth_metrics', {}).get('monthly', {})
        time_ranges = ga_data.get('time_ranges', {})
        
        # Get current week data for detailed analysis
        current_week_data = ga_data.get('current_week', {})
        metric_headers = current_week_data.get('metric_headers', [])
        dimension_headers = current_week_data.get('dimension_headers', [])
        
        # Prepare comparative analysis prompt
        analysis_prompt = f"""Analyze the following Google Analytics 4 data with week-over-week and month-over-month comparisons:

Weekly Comparison ({time_ranges.get('weekly', {}).get('current', {}).get('start')} to {time_ranges.get('weekly', {}).get('current', {}).get('end')}):
{weekly_metrics}

Monthly Comparison ({time_ranges.get('monthly', {}).get('current', {}).get('start')} to {time_ranges.get('monthly', {}).get('current', {}).get('end')}):
{monthly_metrics}

Available Metrics:
{[header.get('name') for header in metric_headers]}

Available Dimensions:
{dimension_headers}

Focus on:
1. Week-over-week performance changes and trends
2. Month-over-month growth patterns
3. Key metrics showing significant changes
4. Areas of improvement or concern
5. Seasonal patterns or anomalies
"""
        
        # Generate analysis
        response = llm.invoke(analysis_prompt)
        state["analysis"] = response.content
        
        return state
        
    except Exception as e:
        logger.error(f"Error analyzing GA data: {str(e)}", exc_info=True)
        raise

def generate_insights(state: ReportState, config: Dict) -> ReportState:
    """Generate insights from GA4 analysis"""
    try:
        logger.info("Generating insights")
        
        # Get analysis and config
        analysis = state.get("analysis", "")
        llm_config = config.get("llm_config", {})
        
        # Initialize LLM with callback manager
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=llm_config.get("temperature", 0.7),
            callbacks=callback_manager.handlers
        )
        
        # Prepare insights prompt
        insights_prompt = f"""Based on the following GA4 analysis, generate key insights:

Analysis:
{analysis}

Focus on:
1. Most significant findings
2. Unexpected patterns
3. Areas of opportunity
4. Potential concerns
5. Notable trends
"""
        
        # Generate insights
        response = llm.invoke(insights_prompt)
        state["insights"] = response.content
        
        return state
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}", exc_info=True)
        raise

def initiate_section_writing(state: ReportState) -> List[str]:
    """Initiate parallel writing of GA4 analysis sections"""
    try:
        logger.info("Initiating section writing")
        
        # Get sections that require analysis
        sections = state.get("sections", [])
        analysis_sections = [s for s in sections if s.research]
        
        if not analysis_sections:
            return []
            
        # For now, just return the next node to process all sections
        return ["write_section"]
        
    except Exception as e:
        logger.error(f"Error initiating section writing: {str(e)}", exc_info=True)
        raise

def initiate_final_section_writing(state: ReportState) -> List[str]:
    """Initiate parallel writing of final sections"""
    try:
        logger.info("Initiating final section writing")
        
        # Get sections that don't require analysis
        sections = state.get("sections", [])
        final_sections = [s for s in sections if not s.research]
        
        if not final_sections:
            logger.info("No final sections to write, skipping to compile_final_report")
            return ["compile_final_report"]
            
        # For now, just return the next node to process all sections
        return ["write_final_sections"]
        
    except Exception as e:
        logger.error(f"Error initiating final section writing: {str(e)}", exc_info=True)
        raise

# Create main graph
graph = StateGraph(ReportState)

# Add output node to convert state to final output
def create_output(state: Dict) -> Dict:
    """Convert final state to output format"""
    # Create output state with final report
    output = {
        "final_report": state.get("final_report", "No report generated")
    }
    logger.info("Created output state with final report")
    return output

graph.add_node("create_output", create_output)

# Add nodes
graph.add_node("fetch_ga_data", fetch_ga_data)
graph.add_node("analyze_data", analyze_ga_data)
graph.add_node("generate_insights", generate_insights)
graph.add_node("generate_report_plan", generate_report_plan)
graph.add_node("write_section", write_section)
graph.add_node("gather_completed_sections", gather_completed_sections)
graph.add_node("write_final_sections", write_final_sections)
graph.add_node("compile_final_report", compile_final_report)

# Add edges
graph.add_edge(START, "fetch_ga_data")
graph.add_edge("fetch_ga_data", "analyze_data")
graph.add_edge("analyze_data", "generate_insights")
graph.add_edge("generate_insights", "generate_report_plan")
graph.add_conditional_edges(
    "generate_report_plan",
    initiate_section_writing,
    ["write_section"]
)
# Add edges for section writing and gathering
graph.add_edge("write_section", "gather_completed_sections")

# Add conditional edges for final sections or direct compilation
graph.add_conditional_edges(
    "gather_completed_sections",
    initiate_final_section_writing,
    ["write_final_sections", "compile_final_report"]
)

# Add edges for final sections path
graph.add_edge("write_final_sections", "compile_final_report")

# Add edges for output conversion
graph.add_edge("compile_final_report", "create_output")
graph.add_edge("create_output", END)

# Compile graph
graph = graph.compile()
