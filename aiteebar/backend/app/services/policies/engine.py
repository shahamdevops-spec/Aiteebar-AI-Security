"""
Policy Evaluation and Enforcement Engine
Evaluates security policies against events and determines enforcement actions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.models import Policy, PolicyAction, PolicyExecution, SecurityEvent
from app.models import PolicyAction as PolicyActionEnum

logger = logging.getLogger(__name__)


class PolicyEvaluationResult:
    """Result of policy evaluation"""
    def __init__(self, policy_id: str, action: PolicyActionEnum, matched: bool, reasoning: str = ""):
        self.policy_id = policy_id
        self.action = action
        self.matched = matched
        self.reasoning = reasoning


class PolicyEngine:
    """Policy evaluation and enforcement engine"""

    @staticmethod
    def evaluate_policies(
        event_data: Dict[str, Any],
        db: Session
    ) -> List[PolicyEvaluationResult]:
        """
        Evaluate all enabled policies against an event.
        Returns policies that matched, ordered by priority.

        Args:
            event_data: Event data to evaluate
            db: Database session

        Returns:
            List of PolicyEvaluationResult ordered by priority
        """
        # Get all enabled policies ordered by priority (lower = higher)
        policies = db.query(Policy).filter(
            Policy.enabled == True
        ).order_by(Policy.priority.asc()).all()

        results = []
        for policy in policies:
            result = PolicyEngine._evaluate_policy(policy, event_data)
            if result.matched:
                results.append(result)
                # Stop at first matching policy (highest priority)
                break

        return results

    @staticmethod
    def _evaluate_policy(policy: Policy, event_data: Dict[str, Any]) -> PolicyEvaluationResult:
        """
        Evaluate a single policy against event data.

        Args:
            policy: Policy to evaluate
            event_data: Event data

        Returns:
            PolicyEvaluationResult with match status
        """
        try:
            condition = policy.condition
            triggers = condition.get("triggers", [])
            logic = condition.get("logic", "AND")

            if not triggers:
                return PolicyEvaluationResult(
                    policy.id,
                    policy.action,
                    False,
                    "No triggers defined in policy"
                )

            # Evaluate all triggers
            trigger_results = []
            for trigger in triggers:
                trigger_matched = PolicyEngine._evaluate_trigger(trigger, event_data)
                trigger_results.append(trigger_matched)

            # Apply logic (AND/OR)
            if logic == "AND":
                policy_matched = all(trigger_results)
                reasoning = f"All {len(triggers)} triggers matched" if policy_matched else f"Not all triggers matched (matched {sum(trigger_results)}/{len(triggers)})"
            else:  # OR
                policy_matched = any(trigger_results)
                reasoning = f"{sum(trigger_results)} of {len(triggers)} triggers matched"

            return PolicyEvaluationResult(
                policy.id,
                policy.action,
                policy_matched,
                reasoning
            )

        except Exception as e:
            logger.error(f"Error evaluating policy {policy.id}: {str(e)}")
            return PolicyEvaluationResult(
                policy.id,
                PolicyActionEnum.ALLOW,
                False,
                f"Policy evaluation error: {str(e)}"
            )

    @staticmethod
    def _evaluate_trigger(trigger: Dict[str, str], event_data: Dict[str, Any]) -> bool:
        """
        Evaluate a single trigger condition.

        Args:
            trigger: Trigger definition with field, operator, value
            event_data: Event data to check

        Returns:
            True if trigger matches, False otherwise
        """
        field = trigger.get("field", "")
        operator = trigger.get("operator", "equals")
        value = trigger.get("value", "")

        event_value = event_data.get(field)

        if event_value is None:
            return False

        try:
            if operator == "equals":
                return str(event_value).lower() == str(value).lower()

            elif operator == "contains":
                return str(value).lower() in str(event_value).lower()

            elif operator == "starts_with":
                return str(event_value).lower().startswith(str(value).lower())

            elif operator == "ends_with":
                return str(event_value).lower().endswith(str(value).lower())

            elif operator == "in":
                # value should be a comma-separated list
                values = [v.strip() for v in str(value).split(",")]
                return str(event_value).lower() in [v.lower() for v in values]

            elif operator == "greater_than":
                return float(event_value) > float(value)

            elif operator == "less_than":
                return float(event_value) < float(value)

            elif operator == "regex":
                import re
                return bool(re.search(str(value), str(event_value)))

            else:
                logger.warning(f"Unknown operator: {operator}")
                return False

        except Exception as e:
            logger.warning(f"Error evaluating trigger: {str(e)}")
            return False

    @staticmethod
    def log_policy_execution(
        policy_id: str,
        event_id: str,
        action: PolicyActionEnum,
        matched_conditions: Dict[str, Any],
        reasoning: str,
        db: Session
    ) -> PolicyExecution:
        """
        Log policy execution for audit trail.

        Args:
            policy_id: ID of executed policy
            event_id: ID of triggering event
            action: Action taken
            matched_conditions: Conditions that matched
            reasoning: Explanation of policy decision
            db: Database session

        Returns:
            Created PolicyExecution record
        """
        execution = PolicyExecution(
            policy_id=policy_id,
            event_id=event_id,
            action_taken=action,
            matched_conditions=matched_conditions,
            reasoning=reasoning,
            executed_at=datetime.utcnow()
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        logger.info(
            f"Policy execution logged: policy_id={policy_id}, "
            f"event_id={event_id}, action={action}, reasoning={reasoning}"
        )

        return execution

    @staticmethod
    def get_policy_statistics(db: Session) -> Dict[str, Any]:
        """
        Get policy statistics and effectiveness metrics.

        Args:
            db: Database session

        Returns:
            Dictionary with policy metrics
        """
        total_policies = db.query(Policy).count()
        enabled_policies = db.query(Policy).filter(Policy.enabled == True).count()
        total_executions = db.query(PolicyExecution).count()

        # Count by action
        action_counts = {}
        for action in PolicyActionEnum:
            count = db.query(PolicyExecution).filter(
                PolicyExecution.action_taken == action
            ).count()
            action_counts[action.value] = count

        return {
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "total_executions": total_executions,
            "executions_by_action": action_counts
        }
