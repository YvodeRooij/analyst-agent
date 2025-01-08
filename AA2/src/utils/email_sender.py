import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_email(subject: str, body: str) -> None:
    """
    Send an email using Gmail SMTP.
    
    Args:
        subject: Email subject
        body: Email body content
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = os.getenv('FROM_EMAIL')
        msg['To'] = os.getenv('GESPREKSEIGENAAR_EMAIL')
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Setup SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login
        server.login(
            os.getenv('EMAIL_USERNAME'),
            os.getenv('EMAIL_PASSWORD')
        )
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Successfully sent email to {msg['To']}")
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        raise
