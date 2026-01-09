from app.models.database import Base, engine
from app.models.db_models import Member
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


def init_db():
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully")


def seed_members():
    from app.models.database import SessionLocal
    db = SessionLocal()
    
    members = [
        Member(
            id="EMP001",
            name="Rajesh Kumar",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="male"
        ),
        Member(
            id="EMP002",
            name="Priya Singh",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="female"
        ),
        Member(
            id="EMP003",
            name="Amit Verma",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="male"
        ),
        Member(
            id="EMP004",
            name="Sneha Reddy",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="female"
        ),
        Member(
            id="EMP005",
            name="Vikram Joshi",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 9, 1),
            annual_limit_used=0.0,
            gender="male"
        ),
        Member(
            id="EMP006",
            name="Kavita Nair",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="female"
        ),
        Member(
            id="EMP007",
            name="Suresh Patil",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="male"
        ),
        Member(
            id="EMP008",
            name="Ravi Menon",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="male"
        ),
        Member(
            id="EMP009",
            name="Anita Desai",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="female"
        ),
        Member(
            id="EMP010",
            name="Deepak Shah",
            policy_id="PLUM_OPD_2024",
            join_date=datetime(2024, 1, 1),
            annual_limit_used=0.0,
            gender="male"
        ),
    ]
    
    try:
        for member in members:
            existing = db.query(Member).filter(Member.id == member.id).first()
            if not existing:
                db.add(member)
        db.commit()
        print(f"[OK] Seeded {len(members)} test members")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding members: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    seed_members()
    print("Database setup complete!")
