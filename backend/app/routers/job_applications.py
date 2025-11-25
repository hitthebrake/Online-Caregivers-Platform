from typing import List

from starlette import status

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_member, get_current_caregiver

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/job_applications", tags=["job_applications"])


@router.post("", response_model=schemas.JobApplicationBase)
def create_job_application(application: schemas.JobApplicationBase, db: Session = Depends(get_db), current_user = Depends(get_current_caregiver)):
    job = db.query(models.JOB).filter(models.JOB.job_id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    caregiver = db.query(models.CAREGIVER).filter(
        models.CAREGIVER.caregiver_user_id == application.caregiver_user_id
    ).first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")

    existing = db.query(models.JOB_APPLICATION).filter(
        models.JOB_APPLICATION.job_id == application.job_id,
        models.JOB_APPLICATION.caregiver_user_id == application.caregiver_user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already exists")

    db_app = models.JOB_APPLICATION(**application.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app


@router.delete("/{job_id}/{caregiver_user_id}", status_code=204)
def delete_job_application(job_id: int, caregiver_user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_caregiver)):
    if not current_user.caregiver_user_id == caregiver_user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to do this")

    app = db.query(models.JOB_APPLICATION).filter(
        models.JOB_APPLICATION.job_id == job_id,
        models.JOB_APPLICATION.caregiver_user_id == caregiver_user_id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Job application not found")

    db.delete(app)
    db.commit()
    return
