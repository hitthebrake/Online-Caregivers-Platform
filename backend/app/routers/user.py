from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=schemas.UserProfile)
async def get_current_user_profile(
        db: Session = Depends(get_db), current_user: models.USER = Depends(auth.get_current_user)
):
    # Determine user type
    caregiver = db.query(models.CAREGIVER).filter(
        models.CAREGIVER.caregiver_user_id == current_user.user_id
    ).first()
    member = db.query(models.MEMBER).filter(
        models.MEMBER.member_user_id == current_user.user_id
    ).first()

    user_type = "caregiver" if caregiver else "member" if member else "unknown"

    return schemas.UserProfile(
        user_id=current_user.user_id,
        email=current_user.email,
        given_name=current_user.given_name,
        surname=current_user.surname,
        city=current_user.city,
        phone_number=current_user.phone_number,
        profile_description=current_user.profile_description,
        user_type=user_type
    )

@router.get("/jobs", response_model=List[schemas.Job])
def get_my_jobs(db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    jobs = db.query(models.JOB).filter(models.JOB.member_user_id == current_user.member_user_id)
    return jobs


@router.get("/job_applications", response_model=List[schemas.ApplicationsForJobOut])
def get_job_applications(db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    member_jobs = db.query(models.JOB).filter(
        models.JOB.member_user_id == current_user.member_user_id
    ).all()

    if not member_jobs:
        return []

    job_ids = [job.job_id for job in member_jobs]

    applications = db.query(models.JOB_APPLICATION).filter(
        models.JOB_APPLICATION.job_id.in_(job_ids)
    ).options(
        joinedload(models.JOB_APPLICATION.job),
        joinedload(models.JOB_APPLICATION.caregiver).joinedload(models.CAREGIVER.user)
    ).all()

    return [
        {
            "caregiver_user_id": app.caregiver_user_id,
            "job": {
                "job_id": app.job_id,
                "member_user_id": app.job.member_user_id,
                "required_caregiving_type": app.job.required_caregiving_type,
                "other_requirements": app.job.other_requirements,
            },
            "date_applied": app.date_applied,
            "email": app.caregiver.user.email,
            "given_name": app.caregiver.user.given_name,
            "surname": app.caregiver.user.surname,
            "city": app.caregiver.user.city,
            "phone_number": app.caregiver.user.phone_number,
            "profile_description": app.caregiver.user.profile_description,
            "photo": app.caregiver.photo,
            "gender": app.caregiver.gender,
            "caregiving_type": app.caregiver.caregiving_type,
            "hourly_rate": app.caregiver.hourly_rate
        }
        for app in applications
    ]


@router.get("/my_applications", response_model=List[schemas.JobApplicationOut])
def get_my_applications(db: Session = Depends(get_db), current_user = Depends(auth.get_current_caregiver)):
    app = db.query(models.JOB_APPLICATION).filter(
        models.JOB_APPLICATION.caregiver_user_id == current_user.caregiver_user_id
    )
    return app


@router.get("/caregiver_appointments", response_model=List[schemas.AppointmentOut])
def read_caregiver_appointments(db: Session = Depends(get_db), current_user = Depends(auth.get_current_caregiver)):
    appointments = db.query(models.APPOINTMENT) \
        .filter(models.APPOINTMENT.caregiver_user_id == current_user.caregiver_user_id) \
        .options(
        joinedload(models.APPOINTMENT.member).joinedload(models.MEMBER.user),
        joinedload(models.APPOINTMENT.member).joinedload(models.MEMBER.addresses)
    )
    context = []
    for appointment in appointments:
        address = appointment.member.addresses[0] if appointment.member.addresses else None

        context.append({
            "appointment_id": appointment.appointment_id,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "work_hours": appointment.work_hours,
            "status": appointment.status,

            "caregiver_user_id": current_user.caregiver_user_id,
            "caregiver_name": current_user.user.given_name,
            "caregiver_surname": current_user.user.surname,
            "caregiver_phone_number": current_user.user.phone_number,
            "caregiver_email": current_user.user.email,

            "member_user_id": appointment.member_user_id,
            "member_name": appointment.member.user.given_name,
            "member_surname": appointment.member.user.surname,
            "member_phone_number": appointment.member.user.phone_number,
            "member_email": appointment.member.user.email,

            "member_address": {
                "house_number": address.house_number if address else "",
                "street": address.street if address else "",
                "town": address.town if address else "",
            }
        })

    return context


@router.get("/member_appointments", response_model=List[schemas.AppointmentOut])
def read_member_appointments(db: Session = Depends(get_db), current_user = Depends(auth.get_current_member)):
    address = db.query(models.ADDRESS).filter(models.ADDRESS.member_user_id == current_user.member_user_id).first()
    appointments = db.query(models.APPOINTMENT) \
                    .filter(models.APPOINTMENT.member_user_id == current_user.member_user_id) \
                    .options(joinedload(models.APPOINTMENT.caregiver).joinedload(models.CAREGIVER.user))
    return [{
        "appointment_id": appointment.appointment_id,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "work_hours": appointment.work_hours,
        "status": appointment.status,

        "caregiver_user_id": appointment.caregiver_user_id,
        "caregiver_name": appointment.caregiver.user.given_name,
        "caregiver_surname": appointment.caregiver.user.surname,
        "caregiver_phone_number": appointment.caregiver.user.phone_number,
        "caregiver_email": appointment.caregiver.user.email,

        "member_user_id": current_user.member_user_id,
        "member_name": current_user.user.given_name,
        "member_surname": current_user.user.surname,
        "member_phone_number": current_user.user.phone_number,
        "member_email": current_user.user.email,

        "member_address": {
            "house_number": address.house_number if address else "",
            "street": address.street if address else "",
            "town": address.town if address else "",
        }
    } for appointment in appointments]

