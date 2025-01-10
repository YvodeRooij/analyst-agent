from fastapi import FastAPI
from langserve import add_routes
from src.flows.report_generation_flow import graph

app = FastAPI(
    title="GA4 Analytics Report API",
    version="1.0",
    description="API for generating GA4 analytics reports using LangGraph"
)

# Add LangServe routes for the graph
add_routes(
    app,
    graph,
    path="/report",
    enable_feedback_endpoint=True
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
