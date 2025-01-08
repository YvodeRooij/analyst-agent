from fastapi import FastAPI, HTTPException, BackgroundTasks
from src.flows.report_generation_flow import graph
from src.models.report_models import ReportStateInput
from typing import Dict, List
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from src.utils.email_sender import send_email
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GA4 Analytics Report API")

# Initialize scheduler
scheduler = AsyncIOScheduler()

async def generate_and_send_report(recipients: List[str] = None):
    """Generate and send weekly report"""
    try:
        logger.info("Generating scheduled weekly report")
        
        # Default input state
        input_data = {
            "property_id": os.getenv("GA_PROPERTY_ID"),
            "report_type": "weekly",
            "recipients": recipients or [os.getenv("GESPREKSEIGENAAR_EMAIL")]
        }
        
        # Generate report
        state_input = ReportStateInput(**input_data)
        result = await graph.ainvoke(state_input)
        
        # Send email
        subject = f"Weekly Analytics Report - {datetime.now().strftime('%Y-%m-%d')}"
        send_email(subject, result["final_report"])
        
        logger.info("Successfully sent weekly report")
        
    except Exception as e:
        logger.error(f"Error generating/sending scheduled report: {str(e)}", exc_info=True)

@app.on_event("startup")
async def start_scheduler():
    """Start the scheduler on app startup"""
    # Schedule weekly report for Friday at 9:00 AM
    scheduler.add_job(
        generate_and_send_report,
        CronTrigger(day_of_week="fri", hour=9, minute=0),
        id="weekly_report",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduled weekly report for Fridays at 9:00 AM")

@app.on_event("shutdown")
async def shutdown_scheduler():
    """Shut down the scheduler on app shutdown"""
    scheduler.shutdown()

@app.post("/generate-report")
async def generate_report(input_data: Dict, background_tasks: BackgroundTasks):
    try:
        # Convert input to ReportStateInput
        state_input = ReportStateInput(**input_data)
        # Invoke graph
        result = await graph.ainvoke(state_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    scheduler_status = "running" if scheduler.running else "stopped"
    next_run = None
    
    # Get next run time for weekly report
    job = scheduler.get_job("weekly_report")
    if job:
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None
    
    return {
        "status": "healthy",
        "scheduler_status": scheduler_status,
        "next_scheduled_report": next_run
    }

@app.post("/schedule-report")
async def schedule_report(schedule: Dict):
    """Endpoint to update report schedule"""
    try:
        # Update schedule
        if "hour" in schedule and "minute" in schedule:
            scheduler.reschedule_job(
                "weekly_report",
                trigger=CronTrigger(
                    day_of_week="fri",
                    hour=schedule["hour"],
                    minute=schedule["minute"]
                )
            )
            return {"message": f"Report rescheduled for Fridays at {schedule['hour']}:{schedule['minute']:02d}"}
        else:
            raise HTTPException(status_code=400, detail="Invalid schedule format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
