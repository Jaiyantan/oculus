"""
Geo Impossible Travel Rule — Tier-1 Deterministic

Detects physically impossible travel between consecutive transactions
using Haversine distance and time delta.
"""
import math
from datetime import datetime, timezone
from .base import FraudRule, RuleResult, RuleTier
from .registry import register_rule


@register_rule
class GeoImpossibleRule(FraudRule):
    name = "geo_rule"
    weight = 0.25
    tier = RuleTier.TIER_1_DETERMINISTIC

    MAX_SPEED_KMH = 900.0  # commercial flight speed, anything above is physically impossible

    def evaluate(self, transaction, profile: dict) -> RuleResult:
        last_loc = profile.get("last_location")

        # Get lat/lon from transaction (handles both object and dict)
        lat = getattr(transaction, 'latitude', None) or (transaction.get('latitude') if isinstance(transaction, dict) else None)
        lon = getattr(transaction, 'longitude', None) or (transaction.get('longitude') if isinstance(transaction, dict) else None)

        if not last_loc or not lat or not lon:
            return RuleResult(
                self.name, False, 0.0,
                "No prior location on record, geo rule skipped",
                self.tier
            )

        lat = float(lat)
        lon = float(lon)

        distance_km = self._haversine(
            last_loc["lat"], last_loc["lon"],
            lat, lon
        )

        time_delta_h = self._hours_since(last_loc["timestamp"])

        if time_delta_h <= 0:
            return RuleResult(
                self.name, False, 0.0,
                "Same timestamp, skipping",
                self.tier
            )

        speed_kmh = distance_km / time_delta_h

        if speed_kmh <= self.MAX_SPEED_KMH:
            return RuleResult(
                self.name, False, 0.0,
                f"Travel speed {speed_kmh:.0f} km/h, within possible range",
                self.tier
            )

        # Score scales with how impossible the speed is
        excess_ratio = min((speed_kmh - self.MAX_SPEED_KMH) / self.MAX_SPEED_KMH, 1.0)
        contribution = self.weight * excess_ratio

        return RuleResult(
            self.name, True, contribution,
            f"Impossible travel speed: {speed_kmh:.0f} km/h ({distance_km:.0f} km in {time_delta_h*60:.0f} min)",
            self.tier
        )

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate great-circle distance between two points in km."""
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _hours_since(self, iso_timestamp: str) -> float:
        """Calculate hours elapsed since the given ISO timestamp."""
        last_time = datetime.fromisoformat(iso_timestamp)
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - last_time
        return delta.total_seconds() / 3600
