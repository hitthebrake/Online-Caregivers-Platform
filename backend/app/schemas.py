from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, time


class UserBase(BaseModel):
    email: str
    given_name: str
    surname: str
    city: Optional[str] = None
    phone_number: Optional[str] = None
    profile_description: Optional[str] = None

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if v and not v.replace('+', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, and +')
        return v


class UserCreate(UserBase):
    password: str


    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    user_id: int
    email: str
    given_name: str
    surname: str
    city: Optional[str] = None
    phone_number: Optional[str] = None
    profile_description: Optional[str] = None
    user_type: str  # 'caregiver' or 'member'

    class Config:
        from_attributes = True


class CaregiverBase(BaseModel):
    photo: Optional[str] = None
    gender: Optional[str] = None
    caregiving_type: Optional[str] = None
    hourly_rate: Optional[float] = None


class Caregiver(CaregiverBase):
    caregiver_user_id: int
    user: UserProfile

    class Config:
        from_attributes = True

class CaregiverUpdate(CaregiverBase):
    caregiver_user_id: int


class MemberBase(BaseModel):
    house_rules: Optional[str] = None
    dependent_description: Optional[str] = None

class MemberUpdate(MemberBase):
    member_user_id: int


class Member(MemberBase):
    member_user_id: int
    user: UserProfile

    class Config:
        from_attributes = True


class AddressBase(BaseModel):
    house_number: Optional[str] = None
    street: Optional[str] = None
    town: Optional[str] = None


class AddressCreate(AddressBase):
    member_user_id: int


class Address(AddressBase):
    member_user_id: int

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    required_caregiving_type: Optional[str] = None
    other_requirements: Optional[str] = None


class JobCreate(JobBase):
    member_user_id: int

    class Config:
        from_attributes = True


class Job(JobBase):
    job_id: int
    member_user_id: int

    class Config:
        from_attributes = True


class JobApplicationBase(BaseModel):
    caregiver_user_id: int
    job_id: int

    class Config:
        from_attributes = True


class JobApplicationOut(JobApplicationBase):
    date_applied: Optional[date] = None


class ApplicationsForJobOut(BaseModel):
    job: Job
    caregiver_user_id: int
    date_applied: Optional[date] = None
    email: str
    given_name: str
    surname: str
    city: Optional[str] = None
    phone_number: Optional[str] = None
    profile_description: Optional[str] = None
    photo: Optional[str] = None
    gender: Optional[str] = None
    caregiving_type: Optional[str] = None
    hourly_rate: Optional[float] = None

    class Config:
        from_attributes = True




class AppointmentBase(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    work_hours: Optional[int] = None
    status: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    caregiver_user_id: int
    member_user_id: int


class AppointmentOut(AppointmentBase):
    appointment_id: int
    caregiver_user_id: int
    caregiver_name: str
    caregiver_surname: str
    caregiver_phone_number: str
    caregiver_email: str
    member_user_id: int
    member_name: str
    member_surname: str
    member_phone_number: str
    member_email: str
    member_address: AddressBase



class Appointment(AppointmentBase):
    appointment_id: int
    caregiver_user_id: int
    member_user_id: int

    class Config:
        from_attributes = True


# Authentication schemas
class UserLogin(BaseModel):
    email: str
    password: str


class CaregiverRegister(BaseModel):
    email: str
    given_name: str
    surname: str
    city: Optional[str] = None
    phone_number: Optional[str] = None
    profile_description: Optional[str] = None
    password: str
    photo: Optional[str] = None
    gender: Optional[str] = None
    caregiving_type: Optional[str] = None
    hourly_rate: Optional[float] = None


class MemberRegister(AddressBase):
    email: str
    given_name: str
    surname: str
    city: Optional[str] = None
    phone_number: Optional[str] = None
    profile_description: Optional[str] = None
    password: str
    house_rules: Optional[str] = None
    dependent_description: Optional[str] = None



class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int