from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.db_models import Member
from app.models.schemas import MemberResponse, MemberCreate

router = APIRouter()


@router.get("/members", response_model=List[MemberResponse])
async def list_members(db: Session = Depends(get_db)):
    members = db.query(Member).all()
    return members


@router.get("/members/{member_id}", response_model=MemberResponse)
async def get_member(member_id: str, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    
    if not member:
        raise HTTPException(status_code=404, detail=f"Member {member_id} not found")
    
    return member


@router.post("/members", response_model=MemberResponse)
async def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    existing = db.query(Member).filter(Member.id == member.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Member {member.id} already exists")
    
    db_member = Member(
        id=member.id,
        name=member.name,
        policy_id=member.policy_id,
        join_date=member.join_date,
        gender=member.gender,
        annual_limit_used=0.0
    )
    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return db_member
