"""
Risk scoring thresholds and rule weights for the Oculus Fraud Engine.
"""

RISK_THRESHOLDS = {
    "auto_block": 0.85,        # blocks transaction, fires SNS/SES notification immediately
    "flag_for_review": 0.45,   # creates fraud_flag, appears in reviewer console
    "log_only": 0.20,          # logged to fraud_flags with tier='log_only', no alert
}

# Rule weights (must sum to 1.0)
RULE_WEIGHTS = {
    "velocity_rule": 0.35,
    "amount_rule": 0.40,
    "geo_rule": 0.25,
}
