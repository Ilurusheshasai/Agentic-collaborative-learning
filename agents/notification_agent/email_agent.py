import os
import smtplib
import socket
import re
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import mimetypes

from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env into os.environ

# Load configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT", "587")  # Keep as string for now
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

# List of required variables and their values
required_env = {
    "SMTP_SERVER": SMTP_SERVER,
    "SMTP_PORT": SMTP_PORT,
    "SMTP_USERNAME": SMTP_USER,
    "SMTP_PASSWORD": SMTP_PASS,
    "FROM_EMAIL": FROM_EMAIL
}

# Identify missing variables
missing_vars = [key for key, value in required_env.items() if not value]

if missing_vars:
    print(f"Error: The following environment variables are missing: {', '.join(missing_vars)}")
    CONFIG_MISSING = True
else:
    CONFIG_MISSING = False

# Convert SMTP_PORT to int if present and valid
try:
    SMTP_PORT = int(SMTP_PORT)
except (TypeError, ValueError):
    print("Error: SMTP_PORT must be an integer.")
    CONFIG_MISSING = True


def convert_markdown_to_html(text):
    """Convert markdown-style formatting to HTML."""
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert *italic* to <em>italic</em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert URLs to proper links
    url_pattern = r'https?://\S+'
    text = re.sub(url_pattern, r'<a href="\g<0>">\g<0></a>', text)
    
    # Convert markdown-style links [text](url) to HTML links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Convert newlines to <br> tags for proper HTML formatting
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    return text


def send_email(to: list[str], subject: str, body: str, attachment_path: str = None) -> bool:
    if CONFIG_MISSING:
        print("Cannot send email due to missing or invalid configuration.")
        return False

    # Create a multipart message
    msg = MIMEMultipart('alternative')
    msg['From'] = FROM_EMAIL
    msg['To'] = ", ".join(to)
    msg['Subject'] = subject
    
    # Prepare both plain text and HTML versions of the message
    plain_text = re.sub(r'\*\*(.*?)\*\*', r'\1', body)  # Remove **bold** markers
    plain_text = re.sub(r'\*(.*?)\*', r'\1', plain_text)  # Remove *italic* markers
    
    # Create HTML version
    html_body = f"""
    <html>
      <head></head>
      <body>
        {convert_markdown_to_html(body)}
      </body>
    </html>
    """
    
    # Attach parts to the message
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header(
                'Content-Disposition', 
                'attachment', 
                filename=os.path.basename(attachment_path)
            )
            msg.attach(attachment)

    # Establish connection and send email
    server = None
    try:
        # Choose correct connection method based on port
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.starttls()  # Only after connection is established
            
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        print(f"Email sent to {', '.join(to)} with subject '{subject}'")
        if attachment_path:
            print(f"Attachment: {attachment_path}")
        return True
        
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
    except socket.gaierror:
        print(f"Error: Could not connect to SMTP server '{SMTP_SERVER}'")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if server:
            try:
                server.quit()
            except:
                pass
    return False