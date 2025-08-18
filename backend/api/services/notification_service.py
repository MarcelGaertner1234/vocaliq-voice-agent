"""
Notification Service
Handles SMS and Email notifications for appointments and confirmations
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from twilio.rest import Client
# import aiosmtplib  # lazy import inside send_email_confirmation
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from api.models.company import Company, Appointment
from api.core.config import get_settings

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for sending notifications via SMS and Email
    """
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize Twilio client
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.twilio_from_number = settings.TWILIO_PHONE_NUMBER
        
        # Email settings (optional)
        self.smtp_host = getattr(settings, "SMTP_HOST", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_user = getattr(settings, "SMTP_USERNAME", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.email_from = getattr(settings, "SMTP_FROM_EMAIL", "noreply@vocaliq.de")
    
    async def send_reservation_confirmation(
        self,
        appointment: Appointment,
        company: Company
    ) -> bool:
        """
        Send reservation confirmation via SMS and/or email
        """
        success = True
        
        # Send SMS if phone number available
        if appointment.customer_phone and appointment.customer_phone != "unknown":
            sms_sent = await self.send_sms_confirmation(appointment, company)
            success = success and sms_sent
        
        # Send email if available
        if appointment.customer_email:
            email_sent = await self.send_email_confirmation(appointment, company)
            success = success and email_sent
        
        # Mark confirmation as sent
        if success:
            appointment.confirmation_sent = True
            # Save in background
            asyncio.create_task(self._update_appointment(appointment))
        
        return success
    
    async def send_sms_confirmation(
        self,
        appointment: Appointment,
        company: Company
    ) -> bool:
        """
        Send SMS confirmation
        """
        if not self.twilio_client:
            logger.warning("Twilio client not configured")
            return False
        
        try:
            # Format message
            message = self._format_sms_confirmation(appointment, company)
            
            # Send SMS
            if company.twilio_phone_number:
                from_number = company.twilio_phone_number
            else:
                from_number = self.twilio_from_number
            
            self.twilio_client.messages.create(
                body=message,
                from_=from_number,
                to=appointment.customer_phone
            )
            
            logger.info(f"SMS confirmation sent to {appointment.customer_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def send_email_confirmation(
        self,
        appointment: Appointment,
        company: Company
    ) -> bool:
        """
        Send email confirmation
        """
        if not self.smtp_host:
            logger.warning("SMTP not configured")
            return False
        
        try:
            # Local import to avoid hard dependency at import time
            import aiosmtplib
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Reservation Confirmation - {company.name}"
            message["From"] = self.email_from
            message["To"] = appointment.customer_email
            
            # Create HTML content
            html_content = self._format_email_confirmation(appointment, company)
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=True
            ) as smtp:
                if self.smtp_user and self.smtp_password:
                    await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"Email confirmation sent to {appointment.customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def send_reminder(
        self,
        appointment: Appointment,
        company: Company,
        hours_before: int = 24
    ) -> bool:
        """
        Send appointment reminder
        """
        # Check if reminder should be sent
        time_until = appointment.scheduled_datetime - datetime.utcnow()
        if time_until.total_seconds() > hours_before * 3600:
            return False  # Too early
        
        if appointment.reminder_sent:
            return False  # Already sent
        
        success = True
        
        # Send SMS reminder
        if appointment.customer_phone and appointment.customer_phone != "unknown":
            sms_sent = await self.send_sms_reminder(appointment, company)
            success = success and sms_sent
        
        # Send email reminder
        if appointment.customer_email:
            email_sent = await self.send_email_reminder(appointment, company)
            success = success and email_sent
        
        # Mark reminder as sent
        if success:
            appointment.reminder_sent = True
            asyncio.create_task(self._update_appointment(appointment))
        
        return success
    
    async def send_sms_reminder(
        self,
        appointment: Appointment,
        company: Company
    ) -> bool:
        """
        Send SMS reminder
        """
        if not self.twilio_client:
            return False
        
        try:
            message = self._format_sms_reminder(appointment, company)
            
            from_number = company.twilio_phone_number or self.twilio_from_number
            
            self.twilio_client.messages.create(
                body=message,
                from_=from_number,
                to=appointment.customer_phone
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS reminder: {e}")
            return False
    
    async def send_email_reminder(
        self,
        appointment: Appointment,
        company: Company
    ) -> bool:
        """
        Send email reminder
        """
        # Similar to send_email_confirmation but with reminder template
        return await self.send_email_confirmation(appointment, company)
    
    def _format_sms_confirmation(
        self,
        appointment: Appointment,
        company: Company
    ) -> str:
        """
        Format SMS confirmation message
        """
        if appointment.appointment_type == "reservation":
            message = f"Reservation confirmed at {company.name}\n"
            message += f"Date: {appointment.scheduled_datetime.strftime('%B %d, %Y')}\n"
            message += f"Time: {appointment.scheduled_datetime.strftime('%I:%M %p')}\n"
            message += f"Party size: {appointment.details.get('party_size', 'N/A')}\n"
            message += f"Confirmation: {appointment.confirmation_code}\n"
            
            if appointment.details.get("special_requests"):
                message += f"Special requests noted.\n"
            
            message += f"Reply CANCEL to cancel."
            
        else:
            message = f"Appointment confirmed at {company.name}\n"
            message += f"Date: {appointment.scheduled_datetime.strftime('%B %d, %Y')}\n"
            message += f"Time: {appointment.scheduled_datetime.strftime('%I:%M %p')}\n"
            message += f"Confirmation: {appointment.confirmation_code}"
        
        return message
    
    def _format_sms_reminder(
        self,
        appointment: Appointment,
        company: Company
    ) -> str:
        """
        Format SMS reminder message
        """
        time_until = appointment.scheduled_datetime - datetime.utcnow()
        hours = int(time_until.total_seconds() / 3600)
        
        if hours > 24:
            when = "tomorrow"
        elif hours > 1:
            when = f"in {hours} hours"
        else:
            when = "soon"
        
        message = f"Reminder: Your reservation at {company.name} is {when}\n"
        message += f"Time: {appointment.scheduled_datetime.strftime('%I:%M %p')}\n"
        message += f"Confirmation: {appointment.confirmation_code}\n"
        message += "Reply CANCEL to cancel."
        
        return message
    
    def _format_email_confirmation(
        self,
        appointment: Appointment,
        company: Company
    ) -> str:
        """
        Format HTML email confirmation
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .details {{ background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .confirmation-code {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
                .footer {{ text-align: center; color: #666; padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reservation Confirmed</h1>
                    <h2>{company.name}</h2>
                </div>
                <div class="content">
                    <p>Dear {appointment.customer_name or 'Guest'},</p>
                    <p>Your reservation has been confirmed!</p>
                    
                    <div class="details">
                        <h3>Reservation Details:</h3>
                        <p><strong>Date:</strong> {appointment.scheduled_datetime.strftime('%A, %B %d, %Y')}</p>
                        <p><strong>Time:</strong> {appointment.scheduled_datetime.strftime('%I:%M %p')}</p>
                        <p><strong>Party Size:</strong> {appointment.details.get('party_size', 'N/A')} guests</p>
                        """
        
        if appointment.details.get("special_requests"):
            html += f"<p><strong>Special Requests:</strong> {appointment.details['special_requests']}</p>"
        
        html += f"""
                        <p><strong>Confirmation Code:</strong></p>
                        <p class="confirmation-code">{appointment.confirmation_code}</p>
                    </div>
                    
                    <p>Please present this confirmation code when you arrive.</p>
                    <p>If you need to cancel or modify your reservation, please call us.</p>
                </div>
                <div class="footer">
                    <p>Thank you for choosing {company.name}!</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def _update_appointment(self, appointment: Appointment):
        """
        Update appointment in database
        """
        from api.core.database import get_session
        
        try:
            async with get_session() as session:
                session.add(appointment)
                await session.commit()
        except Exception as e:
            logger.error(f"Error updating appointment: {e}")