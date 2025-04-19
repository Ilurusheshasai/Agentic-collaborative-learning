import os
import smtplib
import socket
from email.message import EmailMessage
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

def send_email(to: list[str], subject: str, body: str, attachment_path: str = None) -> bool:
    if CONFIG_MISSING:
        print("Cannot send email due to missing or invalid configuration.")
        return False

    # Create message
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(body)

    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        
        with open(attachment_path, "rb") as f:
            data = f.read()
            msg.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(attachment_path)
            )

    # Establish connection and send email
    server = None
    try:
        # Key fix: Choose correct connection method based on port
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
