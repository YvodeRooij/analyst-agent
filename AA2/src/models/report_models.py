from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

class Section(BaseModel):
    """Represents a section of the GA4 analytics report"""
    name: str = Field(description="Name of the section")
    description: str = Field(description="Description of what metrics and dimensions to analyze")
    research: bool = Field(description="Whether this section requires GA4 data analysis", default=True)
    content: Optional[str] = Field(description="The actual content of the section", default=None)

class Sections(BaseModel):
    """Container for multiple sections"""
    sections: List[Section] = Field(description="List of report sections")

class GAData(BaseModel):
    """Container for GA4 data and metadata"""
    date_range: str = Field(description="Time range of the GA4 data")
    metrics: List[str] = Field(description="List of GA4 metrics analyzed")
    dimensions: List[str] = Field(description="List of GA4 dimensions analyzed")
    data: Dict[str, Any] = Field(description="Raw GA4 data")
    error: Optional[str] = Field(description="Error message if GA4 fetch failed", default=None)

class ReportStateInput(BaseModel):
    """Input state for the main graph"""
    property_id: str = Field(description="The GA4 property ID to analyze")

class ReportStateOutput(BaseModel):
    """Output state for the main graph"""
    final_report: str = Field(description="The final compiled analytics report")

class ReportState(TypedDict):
    """State maintained throughout the main graph execution"""
    property_id: str
    ga_data: Dict[str, Any]  # GAData model as dict
    sections: List[Section]
    completed_sections: List[Section]
    analysis: Optional[str]
    insights: Optional[str]
    recommendations: Optional[str]
    report_sections_from_research: Optional[str]
    final_report: Optional[str]

class SectionState(TypedDict):
    """State maintained throughout section subgraph execution"""
    section: Section
    ga_data: Dict[str, Any]  # GAData model as dict
    completed_sections: List[Section]

class SectionOutputState(TypedDict):
    """Output state from section subgraph"""
    completed_sections: List[Section]
