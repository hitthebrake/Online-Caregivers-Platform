from typing import List

from starlette import status

from .. import models, schemas, auth
from ..database import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/caregivers", tags=["caregivers"])


@router.post("", response_model=schemas.UserProfile)
def create_caregiver(caregiver_data: schemas.CaregiverRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == caregiver_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_data = {
        'email': caregiver_data.email,
        'given_name': caregiver_data.given_name,
        'surname': caregiver_data.surname,
        'city': caregiver_data.city,
        'phone_number': caregiver_data.phone_number,
        'profile_description': caregiver_data.profile_description,
        'password': auth.get_password_hash(caregiver_data.password)
    }
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    caregiver_profile_data = {
        'caregiver_user_id': db_user.user_id,
        'photo': caregiver_data.photo,
        'gender': caregiver_data.gender,
        'caregiving_type': caregiver_data.caregiving_type.value if caregiver_data.caregiving_type else None,
        'hourly_rate': caregiver_data.hourly_rate
    }
    db_caregiver = models.Caregiver(**caregiver_profile_data)
    db.add(db_caregiver)
    db.commit()

    return schemas.UserProfile(
        user_id=db_user.user_id,
        email=db_user.email,
        given_name=db_user.given_name,
        surname=db_user.surname,
        city=db_user.city,
        phone_number=db_user.phone_number,
        profile_description=db_user.profile_description,
        user_type="caregiver"
    )


@router.get("", response_model=List[schemas.Caregiver])
def read_caregivers(db: Session = Depends(get_db)):
    caregivers = (db.query(models.Caregiver).options(joinedload(models.Caregiver.user)).all())
    for caregiver in caregivers:
        caregiver.user.user_type = "caregiver"
    return caregivers

@router.get("/my_caregiver_data", response_model=schemas.CaregiverBase)
def get_caregiver(db: Session = Depends(get_db), current_user = Depends(auth.get_current_caregiver)):
    return current_user


@router.put("/my_caregiver_data", response_model=schemas.CaregiverUpdate)
def update_caregiver(caregiver_data: schemas.CaregiverUpdate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_caregiver)):
    if caregiver_data.caregiver_user_id != current_user.caregiver_user_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not allowed")

    caregiver = db.query(models.Caregiver).filter(models.Caregiver.caregiver_user_id == caregiver_data.caregiver_user_id).first()
    update_data = caregiver_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(caregiver, key, value)

    db.commit()
    db.refresh(caregiver)
    return caregiver
