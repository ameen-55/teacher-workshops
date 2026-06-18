"""Email notification service for workshop registration."""
import logging
from flask import current_app
from flask_mail import Message
from app import mail

logger = logging.getLogger(__name__)

import threading

def send_async_email(app_context, msg):
    with app_context:
        try:
            mail.send(msg)
            logger.info(f"Email sent successfully to {msg.recipients[0]}")
        except Exception as exc:
            logger.info(f"Email sending failed (SMTP not configured or timeout). Error: {exc}")

def send_registration_email(teacher_name: str, teacher_email: str,
                            workshop_title: str,
                            is_update: bool = False) -> bool:
    """Send a registration confirmation or update notification email asynchronously."""
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
        
        # Send email asynchronously so it doesn't block the main thread and timeout Gunicorn
        app_context = current_app._get_current_object().app_context()
        thread = threading.Thread(target=send_async_email, args=(app_context, msg))
        thread.start()
        
        return True
    except Exception as exc:
        logger.info(f"Failed to initiate email sending thread. Error: {exc}")
        return False