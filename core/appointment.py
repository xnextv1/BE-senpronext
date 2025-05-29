from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.appointment import Appointment
from models.users import User

# Get appointments by patient
async def get_appointment_by_patient(user_id: int, db: AsyncSession):
    result = await db.execute(select(Appointment).where(Appointment.patient_id == user_id))
    appointment = result.scalars().all()  # ✅ Fix: call .all()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointments found for this patient.")
    return appointment

# Get appointments by therapist
async def get_appointment_by_therapist(user_id: int,db: AsyncSession):
    result = await db.execute(select(Appointment).where(Appointment.therapist_id == user_id))
    appointment = result.scalars().all()  # ✅ Fix: call .all()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointments found for this therapist.")
    return appointment

# Create a new appointment
async def create_appointment_by_therapist(
    patient_id: int,
    therapist_id: int,
    title: str,
    description: str,
    time: datetime,
    db: AsyncSession
):
    appointment = Appointment(
        patient_id=patient_id,
        therapist_id=therapist_id,
        title=title,
        description=description,
        appointment_time=time,
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)  # ✅ Optional: to return the saved instance with generated fields

    return appointment

async def get_possible_therapists(db: AsyncSession):
    result = await db.execute(
        select(User.user_id ,User.email, User.username, User.user_type, User.image, User.description).where(User.user_type == 'therapist')
    )
    therapists = result.all()  # Gets list of tuples (email, username, user_type)

    if not therapists:
        raise HTTPException(status_code=404, detail="No therapists found.")
    therapists_list = [
        {'user_id':user_id, 'email': email, 'username': username, 'user_type': user_type, 'image': image, 'description': description}
        for user_id,email, username, user_type, image, description in therapists
    ]
    return therapists_list
