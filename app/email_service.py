"""Email notification service for workshop registration."""
import logging
from flask import current_app
from flask_mail import Message
from app import mail

logger = logging.getLogger(__name__)

def send_registration_email(teacher_name: str, teacher_email: str,
                            workshop_title: str,
                            is_update: bool = False) -> bool:
    """Send a registration confirmation or update notification email."""
    if is_update:
        subject = f"Update Confirmed – Workshop Registration Modified ({workshop_title})"
    else:
        subject = f"Registration Confirmed – {workshop_title}"

    body = f'''Dear {teacher_name},

Your registration for "{workshop_title}" has been {"updated" if is_update else "confirmed"}.

Thank you.'''

    # Always log the email
    logger.info(f"EMAIL TO: {teacher_email} | SUBJECT: {subject}")
    logger.info(f"BODY: {body}")

    try:
        msg = Message(
            subject=subject,
            recipients=[teacher_email],
        )
        msg.body = body
        mail.send(msg)
        return True
    except Exception as exc:
        logger.info(f"Email sending failed (SMTP not configured). Email content logged above for: {teacher_email}")
        return False