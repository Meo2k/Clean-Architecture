
from src.lib.send_email import send_email
from src.lib.logger import setup_app_level_logger

from src.domain.events.user import PasswordChangedEvent

logger = setup_app_level_logger(__name__)


async def send_email_for_password_change(event: PasswordChangedEvent):
    formatted_time = event.changed_at.strftime("%H:%M ngày %d/%m/%Y")
    
    context = {
        "title": "Bảo mật tài khoản: Mật khẩu đã được thay đổi",
        "email": event.user_email,
        "changed_time": formatted_time,
    }
    
    logger.info(f"[Event] PasswordChangedEvent dispatched for user: {event.user_id}")
    
    # render email
    await send_email(
        to=event.user_email, 
        subject="[InstantNode] Thông báo thay đổi mật khẩu", 
        template_name="user/password_changed_template.html", 
        context=context
    )
