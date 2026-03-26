import pytest
from unittest.mock import MagicMock, patch

from src.core.settings import settings
from src.infras.services.email_service import send_email


@pytest.mark.asyncio
async def test_send_email_skips_when_credentials_missing():
    with patch.object(settings, "EMAIL_USER", None), patch.object(settings, "EMAIL_PASSWORD", None):
        with patch("smtplib.SMTP") as mock_smtp:
            await send_email(
                to="user@example.com",
                subject="Test Subject",
                template_name="user/password_changed_template.html",
                context={"title": "Test", "email": "user@example.com", "changed_time": "12:00"}
            )
            mock_smtp.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_success_with_smtp():
    with patch.object(settings, "EMAIL_USER", "sender@example.com"), \
         patch.object(settings, "EMAIL_PASSWORD", "secret123"), \
         patch.object(settings, "SMTP_HOST", "smtp.custom.com"), \
         patch.object(settings, "SMTP_PORT", 587), \
         patch.object(settings, "SMTP_USE_TLS", True):

        mock_server = MagicMock()
        with patch("smtplib.SMTP", return_value=mock_server) as mock_smtp_cls:
            mock_server.__enter__.return_value = mock_server

            await send_email(
                to="recipient@example.com",
                subject="Password Changed Notification",
                template_name="user/password_changed_template.html",
                context={"title": "Notice", "email": "recipient@example.com", "changed_time": "15:00 31/10/2026"}
            )

            mock_smtp_cls.assert_called_once_with("smtp.custom.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("sender@example.com", "secret123")
            mock_server.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_catches_exception_safely():
    with patch.object(settings, "EMAIL_USER", "sender@example.com"), \
         patch.object(settings, "EMAIL_PASSWORD", "secret123"):

        mock_server = MagicMock()
        mock_server.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("SMTP Auth Failed")

        with patch("smtplib.SMTP", return_value=mock_server):
            # Should not raise exception
            await send_email(
                to="recipient@example.com",
                subject="Password Changed",
                template_name="user/password_changed_template.html",
                context={"title": "Notice", "email": "recipient@example.com", "changed_time": "15:00"}
            )
