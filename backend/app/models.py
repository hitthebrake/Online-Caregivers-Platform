from sqlalchemy import Column, Integer, String, Float, Date, Time, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class USER(Base):
    __tablename__ = "USER"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    given_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    city = Column(String(100))
    phone_number = Column(String(20))
    profile_description = Column(Text)
    password = Column(String(255), nullable=False)

    caregiver = relationship("CAREGIVER", back_populates="user", uselist=False, cascade="all, delete-orphan")
    member = relationship("MEMBER", back_populates="user", uselist=False, cascade="all, delete-orphan")


class CAREGIVER(Base):
    __tablename__ = "caregiver"

    caregiver_user_id = Column(Integer, ForeignKey("USER.user_id", ondelete="CASCADE"), primary_key=True)
    photo = Column(String(500))
    gender = Column(String(20))
    caregiving_type = Column(String(100))
    hourly_rate = Column(Float)

    user = relationship("USER", back_populates="caregiver")
    job_applications = relationship("JOB_APPLICATION", back_populates="caregiver", cascade="all, delete-orphan")
    appointments = relationship("APPOINTMENT", back_populates="caregiver", cascade="all, delete-orphan")


class MEMBER(Base):
    __tablename__ = "member"

    member_user_id = Column(Integer, ForeignKey("USER.user_id", ondelete="CASCADE"), primary_key=True)
    house_rules = Column(Text)
    dependent_description = Column(Text)

    user = relationship("USER", back_populates="member")
    addresses = relationship("ADDRESS", back_populates="member", cascade="all, delete-orphan")
    jobs = relationship("JOB", back_populates="member", cascade="all, delete-orphan")
    appointments = relationship("APPOINTMENT", back_populates="member", cascade="all, delete-orphan")


class ADDRESS(Base):
    __tablename__ = "address"

    member_user_id = Column(Integer, ForeignKey("member.member_user_id", ondelete="CASCADE"), primary_key=True)
    house_number = Column(String(20))
    street = Column(String(255))
    town = Column(String(100))

    member = relationship("MEMBER", back_populates="addresses")


class JOB(Base):
    __tablename__ = "job"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id", ondelete="CASCADE"))
    required_caregiving_type = Column(String(100))
    other_requirements = Column(Text)
    date_posted = Column(Date, server_default=func.current_date())

    member = relationship("MEMBER", back_populates="jobs")
    applications = relationship("JOB_APPLICATION", back_populates="job", cascade="all, delete-orphan")


class JOB_APPLICATION(Base):
    __tablename__ = "job_application"

    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id", ondelete="CASCADE"), primary_key=True)
    job_id = Column(Integer, ForeignKey("job.job_id", ondelete="CASCADE"), primary_key=True)
    date_applied = Column(Date, server_default=func.current_date())

    caregiver = relationship("CAREGIVER", back_populates="job_applications")
    job = relationship("JOB", back_populates="applications")


class APPOINTMENT(Base):
    __tablename__ = "appointment"

    appointment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id", ondelete="CASCADE"))
    member_user_id = Column(Integer, ForeignKey("member.member_user_id", ondelete="CASCADE"))
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Integer)
    status = Column(String(100), default="pending")

    caregiver = relationship("CAREGIVER", back_populates="appointments")
    member = relationship("MEMBER", back_populates="appointments")