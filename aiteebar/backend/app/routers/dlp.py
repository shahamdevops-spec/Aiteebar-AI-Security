"""
DLP Router - API endpoints for Data Loss Prevention scanning and reporting.
Implements RESTful endpoints for text scanning, event retrieval, and reporting.
"""

import time
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DLPEvent, AIAgent
from ..schemas.dlp import (
    DLPScanRequest, DLPScanResponse, DetectedDataSchema,
    DLPEvent as DLPEventSchema, DLPReport, DLPReportRequest,
    DLPEventQuery, SeverityBreakdown, DataTypeBreakdown
)
from ..services.dlp.detector import DLPDetector, DetectedData
from ..services.dlp.patterns import Severity as PatternSeverity

# Initialize detector
detector = DLPDetector()
router = APIRouter(prefix="/api/dlp", tags=["DLP"])


def _severity_to_enum(severity_str: str):
    """Convert severity string to database enum"""
    severity_map = {
        "LOW": "LOW",
        "MEDIUM": "MEDIUM",
        "HIGH": "HIGH",
        "CRITICAL": "CRITICAL",
    }
    return severity_map.get(severity_str, "MEDIUM")


@router.post("/scan", response_model=DLPScanResponse)
async def scan_text(request: DLPScanRequest, db: Session = Depends(get_db)):
    """
    Scan text for sensitive data using pattern matching.

    Args:
        request: DLPScanRequest with text to scan

    Returns:
        DLPScanResponse with detected sensitive data
    """
    try:
        start_time = time.time()

        # Perform detection
        detections = detector.detect_sensitive_data(request.text)

        processing_time = (time.time() - start_time) * 1000

        # Convert detections to response schema
        detected_data_list = [
            DetectedDataSchema(
                data_type=d.data_type.value,
                confidence=d.confidence,
                severity=d.severity.value,
                matched_content=d.matched_content[:20] + "..." if len(d.matched_content) > 20 else d.matched_content,
                context=d.context,
                position=d.position,
            )
            for d in detections
        ]

        # Calculate severity breakdown
        severity_breakdown = {}
        for detection in detections:
            severity = detection.severity.value
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

        # Get unique data types found
        data_types_found = list(set(d.data_type.value for d in detections))

        # If violations found, log to database
        if detections:
            for detection in detections:
                dlp_event = DLPEvent(
                    agent_id=None,  # Will be set by calling service
                    data_type=detection.data_type.value if hasattr(detection.data_type, 'value') else str(detection.data_type),
                    severity=_severity_to_enum(detection.severity.value if hasattr(detection.severity, 'value') else str(detection.severity)),
                    confidence=detection.confidence,
                    matched_context=detection.context,
                    detected_in=request.source or "api_scan",
                    recommended_action="review_and_remediate"
                )
                db.add(dlp_event)
            db.commit()

        return DLPScanResponse(
            success=True,
            scan_id=request.scan_id or f"scan_{int(time.time() * 1000)}",
            timestamp=datetime.utcnow(),
            text_length=len(request.text),
            detections=detected_data_list,
            total_detections=len(detections),
            severity_breakdown=severity_breakdown,
            data_types_found=data_types_found,
            processing_time_ms=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DLP scan failed: {str(e)}")


@router.get("/events", response_model=List[DLPEventSchema])
async def get_dlp_events(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    agent_id: Optional[str] = None,
    severity: Optional[str] = None,
    data_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Retrieve DLP events with optional filtering.

    Args:
        limit: Maximum results to return
        offset: Pagination offset
        agent_id: Filter by agent ID
        severity: Filter by severity level
        data_type: Filter by data type
        days: Include events from last N days

    Returns:
        List of DLP events
    """
    try:
        query = db.query(DLPEvent)

        # Time filter
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(DLPEvent.timestamp >= cutoff_date)

        # Optional filters
        if agent_id:
            query = query.filter(DLPEvent.agent_id == agent_id)
        if severity:
            query = query.filter(DLPEvent.severity == severity)
        if data_type:
            query = query.filter(DLPEvent.data_type == data_type)

        # Order by most recent first
        events = query.order_by(desc(DLPEvent.timestamp)).offset(offset).limit(limit).all()

        # Convert to schema
        return [
            DLPEventSchema(
                id=event.id,
                timestamp=event.timestamp,
                agent_id=event.agent_id,
                agent_name=event.agent.name if event.agent else None,
                source=event.detected_in or "unknown",
                text_preview=event.matched_context[:100] if event.matched_context else "",
                detections=[
                    DetectedDataSchema(
                        data_type=event.data_type,
                        confidence=float(event.confidence) if event.confidence else 0,
                        severity=event.severity,
                        matched_content=event.matched_context[:20] if event.matched_context else "",
                        context=event.matched_context or "",
                        position=0
                    )
                ],
                total_detections=1,
                severity_breakdown={event.severity: 1},
                action_taken=event.recommended_action or "flagged"
            )
            for event in events
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")


@router.get("/report", response_model=DLPReport)
async def get_dlp_report(
    days: int = Query(7, ge=1, le=365),
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get DLP activity summary report.

    Args:
        days: Number of days to report
        agent_id: Filter by agent ID

    Returns:
        DLPReport with statistics and trends
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(DLPEvent).filter(DLPEvent.timestamp >= cutoff_date)

        if agent_id:
            query = query.filter(DLPEvent.agent_id == agent_id)

        events = query.all()

        # Calculate severity breakdown
        severity_breakdown = SeverityBreakdown()
        severity_counts = {}

        for event in events:
            if event.severity:
                severity = event.severity.lower()
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                setattr(severity_breakdown, severity, getattr(severity_breakdown, severity) + 1)

        severity_breakdown.total = len(events)

        # Calculate data type breakdown
        data_type_counts = {}
        for event in events:
            dt = event.data_type
            if dt not in data_type_counts:
                data_type_counts[dt] = {
                    'count': 0,
                    'confidence_sum': 0,
                    'severity': event.severity
                }
            data_type_counts[dt]['count'] += 1
            data_type_counts[dt]['confidence_sum'] += float(event.confidence) if event.confidence else 0

        data_types = [
            DataTypeBreakdown(
                data_type=dt,
                count=data['count'],
                severity=data['severity'],
                confidence_avg=data['confidence_sum'] / data['count'] if data['count'] > 0 else 0
            )
            for dt, data in data_type_counts.items()
        ]

        # Sort by count descending
        data_types.sort(key=lambda x: x.count, reverse=True)
        top_types = [dt.data_type for dt in data_types[:5]]

        # Count unique agents with detections
        agents_with_detections = db.query(func.count(func.distinct(DLPEvent.agent_id))).filter(
            DLPEvent.timestamp >= cutoff_date
        ).scalar() or 0

        # Determine trend (simplified)
        mid_date = cutoff_date + timedelta(days=days/2)
        early_events = db.query(func.count(DLPEvent.id)).filter(
            DLPEvent.timestamp >= cutoff_date,
            DLPEvent.timestamp < mid_date
        ).scalar() or 0
        late_events = db.query(func.count(DLPEvent.id)).filter(
            DLPEvent.timestamp >= mid_date,
            DLPEvent.timestamp <= datetime.utcnow()
        ).scalar() or 0

        if late_events > early_events * 1.1:
            trend = "increasing"
        elif late_events < early_events * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

        return DLPReport(
            report_date=datetime.utcnow(),
            period_days=days,
            total_events=len(events),
            severity_breakdown=severity_breakdown,
            data_types_found=data_types,
            top_detected_types=top_types,
            agents_with_detections=int(agents_with_detections),
            trend=trend
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.post("/scan-agent/{agent_id}")
async def scan_agent_content(
    agent_id: str,
    request: DLPScanRequest,
    db: Session = Depends(get_db)
):
    """
    Scan agent-specific content for sensitive data.
    Associates detections with specific agent.
    """
    # Verify agent exists
    agent = db.query(AIAgent).filter(AIAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        start_time = time.time()
        detections = detector.detect_sensitive_data(request.text)
        processing_time = (time.time() - start_time) * 1000

        # Log all detections to agent
        for detection in detections:
            dlp_event = DLPEvent(
                agent_id=agent_id,
                data_type=detection.data_type.value if hasattr(detection.data_type, 'value') else str(detection.data_type),
                severity=_severity_to_enum(detection.severity.value if hasattr(detection.severity, 'value') else str(detection.severity)),
                confidence=detection.confidence,
                matched_context=detection.context,
                detected_in=request.source or "agent_scan",
                recommended_action="block" if detection.severity == PatternSeverity.CRITICAL else "review"
            )
            db.add(dlp_event)

        db.commit()

        detected_data_list = [
            DetectedDataSchema(
                data_type=d.data_type.value,
                confidence=d.confidence,
                severity=d.severity.value,
                matched_content=d.matched_content[:20] + "..." if len(d.matched_content) > 20 else d.matched_content,
                context=d.context,
                position=d.position,
            )
            for d in detections
        ]

        severity_breakdown = {}
        for detection in detections:
            severity = detection.severity.value
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

        return {
            "success": True,
            "agent_id": agent_id,
            "detections": detected_data_list,
            "total_detections": len(detections),
            "severity_breakdown": severity_breakdown,
            "processing_time_ms": processing_time
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent DLP scan failed: {str(e)}")
