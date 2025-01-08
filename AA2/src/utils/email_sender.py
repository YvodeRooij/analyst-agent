import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import markdown2

logger = logging.getLogger(__name__)

def convert_to_html(text: str) -> str:
    """
    Convert markdown text to styled HTML.
    """
    css = """
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        h2 {
            color: #34495e;
            margin-top: 25px;
        }
        h3 {
            color: #2980b9;
            margin-top: 20px;
        }
        ul, ol {
            margin-left: 20px;
        }
        li {
            margin: 8px 0;
        }
        p {
            margin: 15px 0;
        }
        .metrics {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }
        .highlight {
            background-color: #e8f4f8;
            padding: 2px 5px;
            border-radius: 3px;
        }
    </style>
    """
    
    # Convert markdown to HTML
    html = markdown2.markdown(text, extras=['tables', 'fenced-code-blocks'])
    
    # Wrap with HTML structure and CSS
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        {css}
    </head>
    <body>
        {html}
    </body>
    </html>
    """

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

        # Convert to HTML and add body
        html_content = convert_to_html(body)
        msg.attach(MIMEText(html_content, 'html'))

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
