"""
Alert Delivery
Webhook and email templates for pushing SOC alerts to downstream systems.

Both channels are disabled by default and become active only when the
corresponding ALERT_*_ENABLED setting is turned on.
"""

import logging
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alert, AlertDeliveryStatus

logger = logging.getLogger(__name__)


SEVERITY_COLORS = {
    "CRITICAL": "#b71c1c",
    "HIGH": "#e65100",
    "MEDIUM": "#f9a825",
    "LOW": "#2e7d32",
    "INFO": "#1565c0",
}


class AlertNotifier:
    """Delivers alerts to webhook and email destinations."""

    @staticmethod
    def dispatch(alert: Alert, payload: Dict[str, Any], db: Session) -> Dict[str, str]:
        """
        Send an alert over every enabled channel and record the outcome.

        Returns a per-channel result map. A failure on one channel does not
        prevent the other from being attempted, and never raises — a SOC alert
        that cannot be delivered must still be stored and visible in the UI.
        """
        results: Dict[str, str] = {}

        if settings.alert_webhook_enabled:
            status, error = AlertNotifier.send_webhook(payload)
            results["webhook"] = status.value
            if error:
                results["webhook_error"] = error
        else:
            results["webhook"] = AlertDeliveryStatus.DISABLED.value

        if settings.alert_email_enabled:
            status, error = AlertNotifier.send_email(payload)
            results["email"] = status.value
            if error:
                results["email_error"] = error
        else:
            results["email"] = AlertDeliveryStatus.DISABLED.value

        alert.delivery_status = AlertNotifier._combine(results)
        alert.delivery_error = results.get("webhook_error") or results.get("email_error")
        db.commit()

        return results

    @staticmethod
    def _combine(results: Dict[str, str]) -> AlertDeliveryStatus:
        """Roll per-channel outcomes into a single status for the alert record."""
        channels = [results.get("webhook"), results.get("email")]

        if AlertDeliveryStatus.FAILED.value in channels:
            return AlertDeliveryStatus.FAILED
        if AlertDeliveryStatus.DELIVERED.value in channels:
            return AlertDeliveryStatus.DELIVERED
        return AlertDeliveryStatus.DISABLED

    @staticmethod
    def send_webhook(payload: Dict[str, Any]) -> Tuple[AlertDeliveryStatus, str]:
        """
        POST the alert JSON to the configured collector.

        httpx is imported here rather than at module scope so a missing optional
        dependency degrades this one channel instead of breaking app startup.
        """
        if not settings.alert_webhook_url:
            return AlertDeliveryStatus.FAILED, "ALERT_WEBHOOK_URL is not set"

        try:
            import httpx
        except ImportError:
            return AlertDeliveryStatus.FAILED, "httpx is not installed"

        headers = {"Content-Type": "application/json"}
        if settings.alert_webhook_auth_header:
            headers["Authorization"] = settings.alert_webhook_auth_header

        try:
            response = httpx.post(
                settings.alert_webhook_url,
                json=payload,
                headers=headers,
                timeout=settings.alert_webhook_timeout_seconds,
            )
            response.raise_for_status()
            logger.info("Alert %s delivered to webhook", payload.get("alert_id"))
            return AlertDeliveryStatus.DELIVERED, ""
        except Exception as exc:
            logger.error("Webhook delivery failed for alert %s: %s", payload.get("alert_id"), exc)
            return AlertDeliveryStatus.FAILED, str(exc)

    @staticmethod
    def send_email(payload: Dict[str, Any]) -> Tuple[AlertDeliveryStatus, str]:
        """Send the alert as a multipart email to the configured recipients."""
        if not settings.alert_email_recipients:
            return AlertDeliveryStatus.FAILED, "ALERT_EMAIL_RECIPIENTS is empty"
        if not settings.smtp_host:
            return AlertDeliveryStatus.FAILED, "SMTP_HOST is not set"

        subject, text_body, html_body = AlertNotifier.render_email(payload)

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.alert_email_from
        message["To"] = ", ".join(settings.alert_email_recipients)
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                server.starttls()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)

            logger.info("Alert %s emailed to %d recipient(s)",
                        payload.get("alert_id"), len(settings.alert_email_recipients))
            return AlertDeliveryStatus.DELIVERED, ""
        except Exception as exc:
            logger.error("Email delivery failed for alert %s: %s", payload.get("alert_id"), exc)
            return AlertDeliveryStatus.FAILED, str(exc)

    @staticmethod
    def render_email(payload: Dict[str, Any]) -> Tuple[str, str, str]:
        """Render an alert into (subject, plain-text body, HTML body)."""
        severity = payload.get("severity", "INFO")
        title = payload.get("title", "Security Alert")
        agent = payload.get("agent") or {}
        application = payload.get("application") or {}

        subject = f"[{severity}] {title} - Aiteebar SOC"

        text_body = f"""{severity} SECURITY ALERT

{title}

{payload.get('description', '')}

----------------------------------------
Alert ID:     {payload.get('alert_id')}
Timestamp:    {payload.get('timestamp')}
Risk Score:   {payload.get('risk_score')}/100
Action Taken: {payload.get('action_taken')}
Detected By:  {payload.get('source')}

Agent:        {agent.get('name', 'n/a')} ({agent.get('environment', 'n/a')})
Owner:        {agent.get('owner', 'n/a')}
Application:  {application.get('name', 'n/a')}
Data Type:    {payload.get('data_type', 'n/a')}
Destination:  {payload.get('destination', 'n/a')}

Correlated events: {len(payload.get('events', []))}
----------------------------------------

This alert was generated automatically by Aiteebar AI Security.
"""

        color = SEVERITY_COLORS.get(severity, "#616161")
        rows = [
            ("Alert ID", payload.get("alert_id")),
            ("Timestamp", payload.get("timestamp")),
            ("Risk Score", f"{payload.get('risk_score')}/100"),
            ("Action Taken", payload.get("action_taken")),
            ("Detected By", payload.get("source")),
            ("Agent", agent.get("name", "n/a")),
            ("Owner", agent.get("owner", "n/a")),
            ("Application", application.get("name", "n/a")),
            ("Data Type", payload.get("data_type", "n/a")),
            ("Destination", payload.get("destination", "n/a")),
        ]
        row_html = "".join(
            f'<tr><td style="padding:6px 12px;color:#616161;">{label}</td>'
            f'<td style="padding:6px 12px;font-weight:600;">{value}</td></tr>'
            for label, value in rows
        )

        html_body = f"""<html><body style="font-family:system-ui,sans-serif;background:#f5f5f5;padding:24px;">
  <div style="max-width:640px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;">
    <div style="background:{color};color:#fff;padding:20px 24px;">
      <div style="font-size:12px;letter-spacing:1px;opacity:.85;">{severity} SECURITY ALERT</div>
      <div style="font-size:20px;font-weight:700;margin-top:4px;">{title}</div>
    </div>
    <div style="padding:24px;">
      <p style="margin:0 0 20px;line-height:1.6;color:#333;">{payload.get('description', '')}</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">{row_html}</table>
      <p style="margin-top:20px;font-size:13px;color:#757575;">
        Correlated events: {len(payload.get('events', []))}
      </p>
    </div>
    <div style="padding:16px 24px;background:#fafafa;font-size:12px;color:#9e9e9e;">
      Generated automatically by Aiteebar AI Security.
    </div>
  </div>
</body></html>"""

        return subject, text_body, html_body
