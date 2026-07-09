from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.measurement import Measurement
from app.models.room import Room
from app.schemas.measurement import MeasurementCreate, MeasurementRead, MeasurementUpdate

router = APIRouter(prefix="/rooms/{room_id}/measurements", tags=["Measurements"])


@router.get("", response_model=list[MeasurementRead])
def list_measurements(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")
    return db.query(Measurement).filter(Measurement.room_id == room_id).order_by(Measurement.measured_at.desc()).all()


@router.post("", response_model=MeasurementRead, status_code=201)
def create_measurement(room_id: int, data: MeasurementCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")
    measurement = Measurement(room_id=room_id, **data.model_dump())
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


@router.patch("/{measurement_id}", response_model=MeasurementRead)
def update_measurement(room_id: int, measurement_id: int, data: MeasurementUpdate, db: Session = Depends(get_db)):
    measurement = db.query(Measurement).filter(Measurement.id == measurement_id, Measurement.room_id == room_id).first()
    if not measurement:
        raise HTTPException(404, "Medição não encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(measurement, key, value)
    db.commit()
    db.refresh(measurement)
    return measurement


@router.delete("/{measurement_id}", status_code=204)
def delete_measurement(room_id: int, measurement_id: int, db: Session = Depends(get_db)):
    measurement = db.query(Measurement).filter(Measurement.id == measurement_id, Measurement.room_id == room_id).first()
    if not measurement:
        raise HTTPException(404, "Medição não encontrada")
    db.delete(measurement)
    db.commit()
