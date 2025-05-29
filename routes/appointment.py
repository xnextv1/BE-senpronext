from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from core.appointment import get_appointment_by_therapist, get_appointment_by_patient, create_appointment_by_therapist, \
    get_possible_therapists
from models.appointment import Appointment
from core.db import get_db
from typing import List

router = APIRouter()
load_dotenv()

class AppointmentCreate(BaseModel):
    therapist_id: int
    patient_id: int
    title: str
    description: str
    appointment_time: datetime

@router.get("/patient/schedule")
async def get_appointments_by_user_id(user_id:int,db: AsyncSession = Depends(get_db)):
    result = await get_appointment_by_patient(user_id,db)
    return result

@router.get("/therapist/schedule")
async def get_appointments_by_therapist(therapist_id:int,db:AsyncSession = Depends(get_db)):
    result = await get_appointment_by_therapist(therapist_id,db)
    return result

@router.post("/")
async def create_appointment(appointment: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    result = await create_appointment_by_therapist(db=db, therapist_id=appointment.therapist_id, patient_id=appointment.patient_id, title=appointment.title, description=appointment.description, time=appointment.appointment_time)
    return {"message": "Successfully created appointment"}

@router.get("/therapist")
async def get_appointments(db: AsyncSession = Depends(get_db)):
    result = await get_possible_therapists(db)
    return result