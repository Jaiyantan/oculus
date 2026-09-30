"""
AWS Notifier — publishes high-risk transaction alerts via SNS and SES.

Only fires when risk_tier == 'auto_block' (score >= 0.85).
Wrapped in circuit breaker so a broken AWS service does not crash the hot path.
"""
import json
import os
from .circuit_breaker import CircuitBreaker

sns_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_s=30)


def publish_high_risk_alert(
    transaction_id: str,
    risk_score: float,
    risk_tier: str,
    user_id: str,
    rule_results: list
):
    """
    Publish a high-risk transaction alert.

    In development mode (no SNS_TOPIC_ARN set), logs to console.
    In production, publishes to SNS which fans out to SES email.
    """
    message = {
        "alert_type": "HIGH_RISK_TRANSACTION",
        "transaction_id": transaction_id,
        "user_id": user_id,
        "risk_score": risk_score,
        "risk_tier": risk_tier,
        "triggered_rules": [r["rule_name"] for r in rule_results if r["triggered"]],
        "rule_reasons": [r["reason"] for r in rule_results if r["triggered"]],
    }

    topic_arn = os.environ.get("SNS_TOPIC_ARN", "")

    if not topic_arn:
        # Development mode — log to console
        print(f"\n{'='*60}")
        print(f"🚨 FRAUD ALERT (DEV MODE)")
        print(f"Transaction: {transaction_id}")
        print(f"User: {user_id}")
        print(f"Risk Score: {risk_score}")
        print(f"Risk Tier: {risk_tier}")
        print(f"Triggered Rules: {message['triggered_rules']}")
        print(f"{'='*60}\n")
        return {"status": "logged_dev_mode"}

    try:
        import boto3
        client = boto3.client("sns", region_name=os.environ.get("AWS_REGION", "us-east-1"))

        def _publish():
            return client.publish(
                TopicArn=topic_arn,
                Subject=f"🚨 OCULUS FRAUD ALERT: High-risk transaction (score: {risk_score})",
                Message=json.dumps(message, indent=2)
            )

        result = sns_breaker.call(_publish)
        print(f"[NOTIFICATION] SNS alert published for transaction {transaction_id}")
        return result

    except Exception as e:
        print(f"[NOTIFICATION FAILED] {e}")
        return {"status": "failed", "error": str(e)}
