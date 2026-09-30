"""
Seed demo data — three users with established transaction histories.

Run this once before the demo:
    python seed/seed_demo_data.py

Seeds both PostgreSQL (for record) and Redis (for Tier-1 rule cache).
"""
import sys
import os
import json
import random
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings
from db.session import SessionLocal, engine
from db.base import Base
from models.transaction import Transaction
import redis as redis_lib


# Demo user profiles
DEMO_USERS = {
    "user_demo_alice": {
        "avg_amount": 48.0,
        "stddev": 12.0,
        "base_lat": 40.7128,     # New York
        "base_lon": -74.0060,
        "location_jitter": 0.05,  # ~5km radius
        "num_transactions": 50,
    },
    "user_demo_bob": {
        "avg_amount": 320.0,
        "stddev": 80.0,
        "base_lat": 51.5074,     # London
        "base_lon": -0.1278,
        "location_jitter": 0.08,
        "num_transactions": 50,
    },
    "user_demo_carol": {
        "avg_amount": 1200.0,
        "stddev": 300.0,
        "base_lat": 35.6762,     # Tokyo
        "base_lon": 139.6503,
        "location_jitter": 0.06,
        "num_transactions": 50,
    },
}

MERCHANTS = [
    ("merch_grocery", "groceries"),
    ("merch_gas", "fuel"),
    ("merch_restaurant", "dining"),
    ("merch_online", "e-commerce"),
    ("merch_pharmacy", "healthcare"),
]


def seed_database():
    """Seed PostgreSQL with demo transaction histories."""
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Transaction).filter(
            Transaction.user_id.in_(DEMO_USERS.keys())
        ).count()

        if existing > 0:
            print(f"⚠️  Found {existing} existing demo transactions. Skipping DB seed.")
            print("   Drop tables first if you want to re-seed.")
            return

        print("📝 Seeding demo transactions...")

        for user_id, profile in DEMO_USERS.items():
            print(f"   → {user_id}: {profile['num_transactions']} transactions")

            for i in range(profile["num_transactions"]):
                # Generate realistic transaction data
                amount = max(1.0, random.gauss(profile["avg_amount"], profile["stddev"]))
                merchant = random.choice(MERCHANTS)

                # Timestamps spread over the last 30 days
                hours_ago = random.uniform(1, 720)  # 1 hour to 30 days ago
                created = datetime.now(timezone.utc) - timedelta(hours=hours_ago)

                # Location with jitter around base
                lat = profile["base_lat"] + random.uniform(-profile["location_jitter"], profile["location_jitter"])
                lon = profile["base_lon"] + random.uniform(-profile["location_jitter"], profile["location_jitter"])

                tx = Transaction(
                    user_id=user_id,
                    amount=Decimal(str(round(amount, 2))),
                    currency="USD",
                    merchant_id=merchant[0],
                    merchant_category=merchant[1],
                    latitude=Decimal(str(round(lat, 6))),
                    longitude=Decimal(str(round(lon, 6))),
                    device_fingerprint=f"fp_{user_id}_{random.randint(1, 3)}",
                    ip_address=f"192.168.1.{random.randint(1, 254)}",
                    created_at=created,
                )
                db.add(tx)

        db.commit()
        print("✅ Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"❌ Database seeding failed: {e}")
        raise
    finally:
        db.close()


def seed_redis():
    """Seed Redis with pre-computed user profiles for Tier-1 rules."""
    settings = get_settings()
    r = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        r.ping()
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("   Skipping Redis seed. Rules will work with empty profiles.")
        return

    print("📝 Seeding Redis profiles...")

    for user_id, profile in DEMO_USERS.items():
        print(f"   → {user_id}")

        # Amount stats (Welford's algorithm pre-computed)
        mean = profile["avg_amount"]
        variance = profile["stddev"] ** 2
        count = profile["num_transactions"]
        m2 = variance * count

        r.setex(
            f"user:{user_id}:amount_stats",
            86400,
            json.dumps({
                "mean": mean,
                "variance": variance,
                "count": count,
                "m2": m2,
            })
        )

        # Last location (most recent transaction location)
        lat = profile["base_lat"] + random.uniform(-0.01, 0.01)
        lon = profile["base_lon"] + random.uniform(-0.01, 0.01)
        recent_time = (datetime.now(timezone.utc) - timedelta(minutes=random.randint(5, 30))).isoformat()

        r.setex(
            f"user:{user_id}:last_location",
            3600,
            json.dumps({
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "timestamp": recent_time,
            })
        )

        # Velocity count (start clean — no recent rapid transactions)
        r.delete(f"user:{user_id}:velocity_count")

        # Not blacklisted
        r.delete(f"user:{user_id}:blacklisted")

    print("✅ Redis seeding complete!")


def main():
    print("\n🚀 Oculus Demo Data Seeder")
    print("=" * 40)
    seed_database()
    print()
    seed_redis()
    print("\n✅ All seeding complete! Ready for demo.")
    print("=" * 40)


if __name__ == "__main__":
    main()
