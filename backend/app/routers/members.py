from typing import List

from starlette import status

from .. import models, schemas, auth
from ..database import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=schemas.UserProfile)
def create_member(member_data: schemas.MemberRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.USER).filter(models.USER.email == member_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_data = {
        'email': member_data.email,
        'given_name': member_data.given_name,
        'surname': member_data.surname,
        'city': member_data.city,
        'phone_number': member_data.phone_number,
        'profile_description': member_data.profile_description,
        'password': auth.get_password_hash(member_data.password)
    }
    db_user = models.USER(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    member_profile_data = {
        'member_user_id': db_user.user_id,
        'house_rules': member_data.house_rules,
        'dependent_description': member_data.dependent_description
    }
    db_member = models.MEMBER(**member_profile_data)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    address_data = {
        'member_user_id': db_member.member_user_id,
        'house_number': member_data.house_number,
        'street': member_data.street,
        'town': member_data.town,
    }
    db_address = models.ADDRESS(**address_data)
    db.add(db_address)
    db.commit()


    return schemas.UserProfile(
        user_id=db_user.user_id,
        email=db_user.email,
        given_name=db_user.given_name,
        surname=db_user.surname,
        city=db_user.city,
        phone_number=db_user.phone_number,
        profile_description=db_user.profile_description,
        user_type="member"
    )


@router.get("/my_member_data", response_model=schemas.MemberBase)
def get_member(db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    return current_user


@router.put("/my_member_data", response_model=schemas.MemberUpdate)
def update_member(member_data: schemas.MemberUpdate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    if member_data.member_user_id != current_user.member_user_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not allowed")

    member = db.query(models.MEMBER).filter(models.MEMBER.member_user_id == member_data.member_user_id).first()
    update_data = member_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


@router.get("/my_address_data", response_model=schemas.AddressBase)
def get_address(db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    address = db.query(models.ADDRESS).filter(models.ADDRESS.member_user_id == current_user.member_user_id).first()
    return address or {}


@router.put("/my_address_data", response_model=schemas.Address)
def update_address(address_data: schemas.Address, db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    if address_data.member_user_id != current_user.member_user_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not allowed")

    address = db.query(models.ADDRESS).filter(models.ADDRESS.member_user_id == address_data.member_user_id).first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    update_data = address_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)
    return address


@router.post("/my_address_data", response_model=schemas.Address)
def set_address(address_data: schemas.Address, db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    if address_data.member_user_id != current_user.member_user_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not allowed")

    address = db.query(models.ADDRESS).filter(models.ADDRESS.member_user_id == address_data.member_user_id).first()
    if address:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Address already exists")
    address = models.ADDRESS(**address_data.model_dump(exclude_unset=True))
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.get("", response_model=List[schemas.Member])
def read_members(db: Session = Depends(get_db)):
    members = db.query(models.MEMBER).options(joinedload(models.MEMBER.user)).all()
    for member in members:
        member.user.user_type = "member"
    return members

