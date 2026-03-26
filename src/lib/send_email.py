import smtplib
import asyncio
import os
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

from config import app_config

# setup folder contain template file 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "resources", "templates")
template_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def _send_email_sync(to: str, subject: str, template_name: str, context: dict):
    message = EmailMessage()

    # load html file and render with context
    template = template_env.get_template(template_name)
    html_content = template.render(**context)

    # set content type to html
    message.set_content(html_content, subtype="html")
    message["Subject"] = subject
    message["From"] = app_config.EMAIL_USER
    message["To"] = to

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(app_config.EMAIL_USER, app_config.EMAIL_PASSWORD)
            server.send_message(message)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

async def send_email(to: str, subject: str, template_name: str, context: dict): 
    # push sync task to another thread to not block event loop of FastAPI
    await asyncio.to_thread(_send_email_sync, to, subject, template_name, context)
