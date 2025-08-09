"""
Reservation Action
Handles restaurant table reservations through voice
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, time
import uuid
import pytz

from api.services.actions.base_action import BaseAction, ValidationError
from api.models.company import Company, CompanyIntent, Appointment
from api.core.database import get_session
from api.services.notification_service import NotificationService
from sqlmodel import select

class ReservationAction(BaseAction):
    """
    Action for handling restaurant reservations
    """
    
    def __init__(self, company: Company, intent: CompanyIntent):
        super().__init__(company, intent)
        self.notification_service = NotificationService()
    
    async def validate_parameters(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate reservation parameters
        """
        validated = {}
        
        # Validate date
        if not entities.get("date"):
            raise ValidationError("What date would you like to make a reservation for?")
        
        # Parse date
        date_str = entities["date"]
        if isinstance(date_str, str):
            if date_str == "today":
                reservation_date = datetime.now().date()
            elif date_str == "tomorrow":
                reservation_date = (datetime.now() + timedelta(days=1)).date()
            else:
                try:
                    reservation_date = datetime.fromisoformat(date_str).date()
                except:
                    raise ValidationError("I couldn't understand the date. Could you please specify it again?")
        else:
            reservation_date = date_str
        
        validated["date"] = reservation_date
        
        # Validate time
        if not entities.get("time"):
            raise ValidationError("What time would you like to reserve?")
        
        # Parse time
        time_str = entities["time"]
        if isinstance(time_str, str):
            # Handle relative times
            if time_str == "evening":
                reservation_time = time(19, 0)  # Default to 7 PM
            elif time_str == "afternoon":
                reservation_time = time(14, 0)  # Default to 2 PM
            elif time_str == "morning":
                reservation_time = time(10, 0)  # Default to 10 AM
            else:
                try:
                    # Parse time string
                    if ":" in time_str:
                        parts = time_str.replace("am", "").replace("pm", "").strip().split(":")
                        hour = int(parts[0])
                        minute = int(parts[1]) if len(parts) > 1 else 0
                        
                        if "pm" in time_str.lower() and hour < 12:
                            hour += 12
                        elif "am" in time_str.lower() and hour == 12:
                            hour = 0
                        
                        reservation_time = time(hour, minute)
                    else:
                        # Just hour
                        hour = int(time_str.replace("am", "").replace("pm", "").strip())
                        if "pm" in time_str.lower() and hour < 12:
                            hour += 12
                        reservation_time = time(hour, 0)
                except:
                    raise ValidationError("I couldn't understand the time. Could you please specify it again?")
        else:
            reservation_time = time_str
        
        validated["time"] = reservation_time
        
        # Combine date and time
        validated["datetime"] = datetime.combine(reservation_date, reservation_time)
        
        # Check if in the future
        if validated["datetime"] <= datetime.now():
            raise ValidationError("The reservation time must be in the future.")
        
        # Validate party size
        if not entities.get("party_size"):
            raise ValidationError("How many people will be in your party?")
        
        try:
            party_size = int(entities["party_size"])
            if party_size < 1:
                raise ValueError()
            if party_size > 20:
                raise ValidationError("For parties larger than 20, please call us directly.")
        except:
            raise ValidationError("Could you please tell me the number of people?")
        
        validated["party_size"] = party_size
        
        # Optional fields
        validated["customer_name"] = entities.get("customer_name")
        validated["customer_phone"] = entities.get("customer_phone")
        validated["special_requests"] = entities.get("special_requests")
        validated["seating_preference"] = entities.get("seating_preference")
        
        # Check business hours
        if not self._is_within_business_hours(validated["datetime"]):
            raise ValidationError("I'm sorry, but that time is outside our business hours.")
        
        return validated
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the reservation
        """
        # Check availability
        is_available = await self._check_availability(
            parameters["datetime"],
            parameters["party_size"]
        )
        
        if not is_available:
            # Suggest alternative times
            alternatives = await self._find_alternative_times(
                parameters["datetime"],
                parameters["party_size"]
            )
            
            return {
                "status": "unavailable",
                "requested_time": parameters["datetime"],
                "alternatives": alternatives
            }
        
        # Create reservation
        async with get_session() as session:
            appointment = Appointment(
                company_id=self.company.id,
                customer_phone=parameters.get("customer_phone", "unknown"),
                customer_name=parameters.get("customer_name"),
                appointment_type="reservation",
                scheduled_datetime=parameters["datetime"],
                duration_minutes=120,  # Default 2 hour reservation
                details={
                    "party_size": parameters["party_size"],
                    "seating_preference": parameters.get("seating_preference"),
                    "special_requests": parameters.get("special_requests")
                },
                status="confirmed",
                confirmation_code=self._generate_confirmation_code()
            )
            
            session.add(appointment)
            await session.commit()
            await session.refresh(appointment)
        
        # Send confirmation
        if parameters.get("customer_phone"):
            await self.notification_service.send_reservation_confirmation(
                appointment,
                self.company
            )
        
        return {
            "status": "confirmed",
            "appointment": appointment,
            "confirmation_code": appointment.confirmation_code
        }
    
    async def generate_response(self, result: Dict[str, Any]) -> str:
        """
        Generate voice response for reservation result
        """
        if result["status"] == "confirmed":
            appointment = result["appointment"]
            response = f"Perfect! I've confirmed your reservation for {appointment.details['party_size']} "
            response += f"on {self.format_date(appointment.scheduled_datetime)} "
            response += f"at {self.format_time(appointment.scheduled_datetime)}. "
            response += f"Your confirmation code is {appointment.confirmation_code}. "
            
            if appointment.customer_phone and appointment.customer_phone != "unknown":
                response += "You'll receive a confirmation text shortly. "
            
            response += "We look forward to seeing you!"
            
            return response
            
        elif result["status"] == "unavailable":
            alternatives = result["alternatives"]
            response = "I'm sorry, but that time is not available. "
            
            if alternatives:
                response += "I have these alternatives available: "
                for i, alt in enumerate(alternatives[:3], 1):
                    response += f"Option {i}: {self.format_time(alt)}. "
                response += "Would any of these work for you?"
            else:
                response += "Would you like to try a different date or time?"
            
            return response
        
        return "There was an issue with your reservation. Please try again."
    
    async def generate_confirmation_request(self, parameters: Dict[str, Any]) -> str:
        """
        Generate confirmation request
        """
        response = f"Let me confirm: You'd like a table for {parameters['party_size']} "
        response += f"on {self.format_date(parameters['datetime'])} "
        response += f"at {self.format_time(parameters['datetime'])}. "
        
        if parameters.get("special_requests"):
            response += f"With special requests: {parameters['special_requests']}. "
        
        response += "Is this correct?"
        
        return response
    
    def _is_within_business_hours(self, dt: datetime) -> bool:
        """
        Check if datetime is within business hours
        """
        if not self.company.business_hours:
            return True  # No hours configured, allow all times
        
        day_name = dt.strftime("%A").lower()
        day_hours = self.company.business_hours.get(day_name)
        
        if not day_hours or day_hours == "closed":
            return False
        
        # Parse hours (format: "11:00 AM - 10:00 PM")
        try:
            parts = day_hours.split(" - ")
            open_time = datetime.strptime(parts[0], "%I:%M %p").time()
            close_time = datetime.strptime(parts[1], "%I:%M %p").time()
            
            return open_time <= dt.time() <= close_time
        except:
            return True  # Can't parse, allow
    
    async def _check_availability(
        self,
        requested_time: datetime,
        party_size: int
    ) -> bool:
        """
        Check if requested time is available
        """
        # Get restaurant capacity from company settings
        max_capacity = self.company.settings.get("restaurant_capacity", 100)
        max_tables = self.company.settings.get("max_tables", 20)
        
        # Check existing reservations
        async with get_session() as session:
            # Get reservations within 2 hours of requested time
            start_window = requested_time - timedelta(hours=1)
            end_window = requested_time + timedelta(hours=2)
            
            result = await session.execute(
                select(Appointment)
                .where(Appointment.company_id == self.company.id)
                .where(Appointment.appointment_type == "reservation")
                .where(Appointment.status.in_(["confirmed", "pending"]))
                .where(Appointment.scheduled_datetime >= start_window)
                .where(Appointment.scheduled_datetime <= end_window)
            )
            existing_reservations = result.scalars().all()
            
            # Calculate total capacity at requested time
            total_guests = sum(
                r.details.get("party_size", 2)
                for r in existing_reservations
                if abs((r.scheduled_datetime - requested_time).total_seconds()) < 3600
            )
            
            # Check if we have capacity
            if total_guests + party_size > max_capacity:
                return False
            
            # Check if we have tables available
            if len(existing_reservations) >= max_tables:
                return False
        
        return True
    
    async def _find_alternative_times(
        self,
        requested_time: datetime,
        party_size: int
    ) -> List[datetime]:
        """
        Find alternative available times
        """
        alternatives = []
        
        # Check times in 30-minute increments
        for offset in [-60, -30, 30, 60, 90, 120]:  # -1hr to +2hrs
            alt_time = requested_time + timedelta(minutes=offset)
            
            # Skip if in the past
            if alt_time <= datetime.now():
                continue
            
            # Check if within business hours
            if not self._is_within_business_hours(alt_time):
                continue
            
            # Check availability
            if await self._check_availability(alt_time, party_size):
                alternatives.append(alt_time)
            
            if len(alternatives) >= 3:
                break
        
        return alternatives
    
    def _generate_confirmation_code(self) -> str:
        """
        Generate a unique confirmation code
        """
        return str(uuid.uuid4())[:8].upper()