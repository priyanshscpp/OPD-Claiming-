from datetime import datetime, timedelta
from typing import Optional
import re


def days_between(date1: datetime, date2: datetime) -> int:
    return abs((date2 - date1).days)


def add_days(date: datetime, days: int) -> datetime:
    return date + timedelta(days=days)


def subtract_days(date: datetime, days: int) -> datetime:
    return date - timedelta(days=days)


def validate_doctor_registration(reg_number: str) -> bool:
    pattern = r'^[A-Z]{2,5}\/\d{5}\/\d{4}$'
    return bool(re.match(pattern, reg_number))


def calculate_name_similarity(name1: str, name2: str) -> float:
    if not name1 or not name2:
        return 0.0
    
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    
    if name1 == name2:
        return 1.0
    
    words1 = set(name1.split())
    words2 = set(name2.split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def format_currency(amount: float) -> str:
    return f"₹{amount:,.2f}"


def generate_claim_id() -> str:
    import uuid
    return f"CLM_{uuid.uuid4().hex[:8].upper()}"
