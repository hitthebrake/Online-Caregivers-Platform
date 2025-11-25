from typing import List

from starlette import status

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_member, get_current_caregiver

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=schemas.Job)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db), current_user = Depends(get_current_member)):
    member = db.query(models.MEMBER).filter(models.MEMBER.member_user_id == job.member_user_id).first()
    if not member:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )
    if job.member_user_id != current_user.member_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized!"
        )

    db_job = models.JOB(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("", response_model=List[schemas.Job])
def read_jobs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    jobs = db.query(models.JOB).all()
    return jobs


@router.put("/{job_id}", response_model=schemas.Job)
def update_job(
    job_id: int,
    job_update: schemas.JobBase,
    db: Session = Depends(get_db),
    current_user: models.MEMBER = Depends(get_current_member)
):
    job = db.query(models.JOB).filter(models.JOB.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.member_user_id != current_user.member_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this job"
        )

    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    job = db.query(models.JOB).filter(models.JOB.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.member_user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this job"
        )

    db.delete(job)
    db.commit()
    return




