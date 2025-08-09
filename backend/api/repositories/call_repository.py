"""
Call Repository für VocalIQ
Datenzugriff für Call-Log und Call-Analytics Entities
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc

from api.models.database import CallLog, CallStatus, CallDirection, CallAnalytics
from api.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CallRepository(BaseRepository[CallLog]):
    """Repository für CallLog-Entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CallLog)
    
    async def get_by_twilio_sid(self, twilio_call_sid: str) -> Optional[CallLog]:
        """Get call by Twilio Call SID"""
        result = await self.session.execute(
            select(CallLog).where(CallLog.twilio_call_sid == twilio_call_sid)
        )
        return result.scalar_one_or_none()
    
    async def create_call(
        self,
        twilio_call_sid: str,
        organization_id: int,
        direction: CallDirection,
        from_number: str,
        to_number: str,
        status: CallStatus = CallStatus.INITIATED,
        **kwargs
    ) -> CallLog:
        """Create new call log entry"""
        call_data = {
            "twilio_call_sid": twilio_call_sid,
            "organization_id": organization_id,
            "direction": direction,
            "from_number": from_number,
            "to_number": to_number,
            "status": status,
            **kwargs
        }
        
        call = CallLog(**call_data)
        self.session.add(call)
        await self.session.commit()
        await self.session.refresh(call)
        
        logger.info(f"📞 Created call log: {twilio_call_sid} ({direction})")
        return call
    
    async def update_call_status(
        self, 
        twilio_call_sid: str, 
        status: CallStatus,
        **additional_data
    ) -> Optional[CallLog]:
        """Update call status and additional data"""
        call = await self.get_by_twilio_sid(twilio_call_sid)
        if not call:
            return None
        
        update_data = {"status": status, **additional_data}
        
        # Add timing data based on status
        now = datetime.now(timezone.utc)
        if status == CallStatus.ANSWERED and not call.answer_time:
            update_data["answer_time"] = now
        elif status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.CANCELLED] and not call.end_time:
            update_data["end_time"] = now
            
            # Calculate duration if we have start and end times
            if call.start_time:
                duration = (now - call.start_time).total_seconds()
                update_data["duration_seconds"] = int(duration)
                
                # Billable duration (exclude first 6 seconds for connection)
                billable_duration = max(0, int(duration) - 6)
                update_data["billable_seconds"] = billable_duration
        
        return await self.update(call.id, update_data)
    
    async def get_calls_by_organization(
        self,
        organization_id: int,
        status: Optional[CallStatus] = None,
        direction: Optional[CallDirection] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[CallLog]:
        """Get calls by organization with filters"""
        query = select(CallLog).where(CallLog.organization_id == organization_id)
        
        if status:
            query = query.where(CallLog.status == status)
        
        if direction:
            query = query.where(CallLog.direction == direction)
        
        if start_date:
            query = query.where(CallLog.created_at >= start_date)
        
        if end_date:
            query = query.where(CallLog.created_at <= end_date)
        
        query = query.order_by(desc(CallLog.created_at)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_calls_by_phone_number(
        self,
        phone_number: str,
        direction: Optional[CallDirection] = None,
        days_back: int = 30,
        offset: int = 0,
        limit: int = 100
    ) -> List[CallLog]:
        """Get calls involving a specific phone number"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        query = select(CallLog).where(
            and_(
                or_(
                    CallLog.from_number == phone_number,
                    CallLog.to_number == phone_number
                ),
                CallLog.created_at >= cutoff_date
            )
        )
        
        if direction:
            query = query.where(CallLog.direction == direction)
        
        query = query.order_by(desc(CallLog.created_at)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_active_calls(self, organization_id: Optional[int] = None) -> List[CallLog]:
        """Get currently active calls"""
        query = select(CallLog).where(
            CallLog.status.in_([CallStatus.INITIATED, CallStatus.RINGING, CallStatus.ANSWERED, CallStatus.IN_PROGRESS])
        )
        
        if organization_id:
            query = query.where(CallLog.organization_id == organization_id)
        
        query = query.order_by(desc(CallLog.created_at))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_call_statistics(
        self,
        organization_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive call statistics"""
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(timezone.utc)
        
        base_query = select(CallLog).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.created_at >= start_date,
                CallLog.created_at <= end_date
            )
        )
        
        # Total calls
        total_result = await self.session.execute(
            select(func.count(CallLog.id)).select_from(base_query.subquery())
        )
        total_calls = total_result.scalar()
        
        # Calls by status
        status_query = select(
            CallLog.status,
            func.count(CallLog.id).label('count')
        ).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.created_at >= start_date,
                CallLog.created_at <= end_date
            )
        ).group_by(CallLog.status)
        
        status_result = await self.session.execute(status_query)
        status_counts = {row.status: row.count for row in status_result}
        
        # Calls by direction
        direction_query = select(
            CallLog.direction,
            func.count(CallLog.id).label('count')
        ).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.created_at >= start_date,
                CallLog.created_at <= end_date
            )
        ).group_by(CallLog.direction)
        
        direction_result = await self.session.execute(direction_query)
        direction_counts = {row.direction: row.count for row in direction_result}
        
        # Duration statistics
        duration_query = select(
            func.avg(CallLog.duration_seconds).label('avg_duration'),
            func.sum(CallLog.duration_seconds).label('total_duration'),
            func.max(CallLog.duration_seconds).label('max_duration')
        ).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.created_at >= start_date,
                CallLog.created_at <= end_date,
                CallLog.duration_seconds.isnot(None)
            )
        )
        
        duration_result = await self.session.execute(duration_query)
        duration_stats = duration_result.first()
        
        # Cost statistics
        cost_query = select(
            func.sum(CallLog.cost).label('total_cost'),
            func.avg(CallLog.cost).label('avg_cost')
        ).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.created_at >= start_date,
                CallLog.created_at <= end_date,
                CallLog.cost.isnot(None)
            )
        )
        
        cost_result = await self.session.execute(cost_query)
        cost_stats = cost_result.first()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "totals": {
                "total_calls": total_calls,
                "answered_calls": status_counts.get(CallStatus.ANSWERED, 0) + status_counts.get(CallStatus.COMPLETED, 0),
                "missed_calls": status_counts.get(CallStatus.FAILED, 0) + status_counts.get(CallStatus.CANCELLED, 0),
                "inbound_calls": direction_counts.get(CallDirection.INBOUND, 0),
                "outbound_calls": direction_counts.get(CallDirection.OUTBOUND, 0)
            },
            "status_breakdown": status_counts,
            "direction_breakdown": direction_counts,
            "duration": {
                "avg_duration_seconds": int(duration_stats.avg_duration or 0),
                "total_duration_seconds": int(duration_stats.total_duration or 0),
                "max_duration_seconds": int(duration_stats.max_duration or 0),
                "avg_duration_minutes": round((duration_stats.avg_duration or 0) / 60, 1),
                "total_duration_hours": round((duration_stats.total_duration or 0) / 3600, 1)
            },
            "costs": {
                "total_cost": float(cost_stats.total_cost or 0),
                "avg_cost_per_call": float(cost_stats.avg_cost or 0),
                "currency": "EUR"
            },
            "metrics": {
                "answer_rate": round((status_counts.get(CallStatus.ANSWERED, 0) + status_counts.get(CallStatus.COMPLETED, 0)) / total_calls * 100, 1) if total_calls > 0 else 0,
                "completion_rate": round(status_counts.get(CallStatus.COMPLETED, 0) / total_calls * 100, 1) if total_calls > 0 else 0
            }
        }
    
    async def get_hourly_call_volume(
        self,
        organization_id: int,
        date: datetime
    ) -> List[Dict[str, Any]]:
        """Get call volume by hour for a specific date"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        query = select(
            func.extract('hour', CallLog.created_at).label('hour'),
            func.count(CallLog.id).label('call_count'),
            CallLog.direction
        ).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.created_at >= start_date,
                CallLog.created_at < end_date
            )
        ).group_by(
            func.extract('hour', CallLog.created_at),
            CallLog.direction
        ).order_by(asc('hour'))
        
        result = await self.session.execute(query)
        
        # Initialize 24-hour structure
        hourly_data = []
        for hour in range(24):
            hourly_data.append({
                "hour": hour,
                "inbound_calls": 0,
                "outbound_calls": 0,
                "total_calls": 0
            })
        
        # Fill in actual data
        for row in result:
            hour_idx = int(row.hour)
            if row.direction == CallDirection.INBOUND:
                hourly_data[hour_idx]["inbound_calls"] = row.call_count
            else:
                hourly_data[hour_idx]["outbound_calls"] = row.call_count
            
            hourly_data[hour_idx]["total_calls"] = (
                hourly_data[hour_idx]["inbound_calls"] + 
                hourly_data[hour_idx]["outbound_calls"]
            )
        
        return hourly_data
    
    async def update_ai_processing_data(
        self,
        call_id: int,
        transcription: Optional[str] = None,
        transcription_confidence: Optional[float] = None,
        ai_summary: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        call_purpose: Optional[str] = None
    ) -> Optional[CallLog]:
        """Update AI-generated data for a call"""
        update_data = {}
        
        if transcription is not None:
            update_data["transcription"] = transcription
        if transcription_confidence is not None:
            update_data["transcription_confidence"] = transcription_confidence
        if ai_summary is not None:
            update_data["ai_summary"] = ai_summary
        if sentiment_score is not None:
            update_data["sentiment_score"] = sentiment_score
        if call_purpose is not None:
            update_data["call_purpose"] = call_purpose
        
        if update_data:
            result = await self.update(call_id, update_data)
            logger.info(f"🤖 Updated AI data for call ID: {call_id}")
            return result
        
        return None
    
    async def mark_for_follow_up(
        self,
        call_id: int,
        follow_up_notes: str,
        lead_status: Optional[str] = None
    ) -> Optional[CallLog]:
        """Mark call for follow-up"""
        update_data = {
            "follow_up_required": True,
            "follow_up_notes": follow_up_notes
        }
        
        if lead_status:
            update_data["lead_status"] = lead_status
        
        result = await self.update(call_id, update_data)
        if result:
            logger.info(f"📝 Marked call ID {call_id} for follow-up")
        
        return result
    
    async def get_calls_requiring_follow_up(
        self,
        organization_id: int,
        offset: int = 0,
        limit: int = 100
    ) -> List[CallLog]:
        """Get calls that require follow-up"""
        query = select(CallLog).where(
            and_(
                CallLog.organization_id == organization_id,
                CallLog.follow_up_required == True
            )
        ).order_by(desc(CallLog.created_at)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()