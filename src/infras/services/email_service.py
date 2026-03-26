import smtplib
import asyncio
import os
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

from src.core.settings import settings, ROOT_PATH
from src.core.logger import setup_app_level_logger

logger = setup_app_level_logger(__name__)

# Setup folder containing template files
TEMPLATES_DIR = os.path.join(ROOT_PATH, "src", "resources", "templates")
template_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def _send_email_sync(to: str, subject: str, template_name: str, context: dict):
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        logger.warning(f"Email credentials not configured. Skipping sending email to {to}")
        return

    message = EmailMessage()

    # Load html template file and render with context
    template = template_env.get_template(template_name)
    html_content = template.render(**context)

    # Set content type to html
    message.set_content(html_content, subtype="html")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_USER
    message["To"] = to

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.send_message(message)
            logger.info(f"Email sent successfully to {to} (Subject: {subject})")
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}", exc_info=True)


async def send_email(to: str, subject: str, template_name: str, context: dict): 
    """Push sync SMTP task to a worker thread to avoid blocking FastAPI's async event loop."""
    await asyncio.to_thread(_send_email_sync, to, subject, template_name, context)
