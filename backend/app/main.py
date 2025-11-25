from fastapi import FastAPI
from starlette.responses import JSONResponse

from . import models
from .database import get_db, engine
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, caregivers, members, appointments, jobs, job_applications

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from . import schemas, auth

models.Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Caregiver Platform API", version="1.0.0")
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app = FastAPI(title="Caregiver Platform API")

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

# Add your frontend domain when deployed
# if os.getenv("RENDER"):
#     origins.append("https://your-frontend-domain.render.com")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(caregivers.router, tags=["caregivers"])
app.include_router(members.router, tags=["members"])
app.include_router(jobs.router, tags=["jobs"])
app.include_router(appointments.router, tags=["appointments"])
app.include_router(user.router, tags=["user"])
app.include_router(job_applications.router, tags=["job_applications"])


@app.get("/")
async def health_check():
    return JSONResponse({"status": "ok"})

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    cur_user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not cur_user or not auth.verify_password(login_data.password, cur_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Determine user type
    caregiver = db.query(models.Caregiver).filter(models.Caregiver.caregiver_user_id == cur_user.user_id).first()
    member = db.query(models.Member).filter(models.Member.member_user_id == cur_user.user_id).first()

    user_type = "caregiver" if caregiver else "member" if member else "unknown"

    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": cur_user.email, "user_type": user_type},
        expires_delta=access_token_expires
    )

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user_type,
        user_id=cur_user.user_id
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
