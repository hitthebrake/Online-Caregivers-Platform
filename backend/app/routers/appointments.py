from typing import List
from .. import models, schemas, auth
from ..database import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    if appointment.member_user_id != current_user.member_user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action.")


    db_appointment = models.APPOINTMENT(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@router.put("/{appointment_id}/{status}", response_model=schemas.Appointment)
def update_appointment_status(appointment_id: int, status: str, db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    appointment = db.query(models.APPOINTMENT).filter(
        models.APPOINTMENT.appointment_id == appointment_id,
        models.APPOINTMENT.member_user_id == current_user.member_user_id,
    ).first()
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = status
    db.commit()
    db.refresh(appointment)
    return appointment
