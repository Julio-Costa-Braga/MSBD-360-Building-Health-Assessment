from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import Inspection
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate

router = APIRouter(prefix="/inspections/{inspection_id}/rooms", tags=["Rooms"])


@router.get("", response_model=list[RoomRead])
def list_rooms(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")
    return db.query(Room).filter(Room.inspection_id == inspection_id).all()


@router.post("", response_model=RoomRead, status_code=201)
def create_room(inspection_id: int, data: RoomCreate, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")
    room = Room(inspection_id=inspection_id, **data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.patch("/{room_id}", response_model=RoomRead)
def update_room(inspection_id: int, room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id, Room.inspection_id == inspection_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
def delete_room(inspection_id: int, room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id, Room.inspection_id == inspection_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")
    db.delete(room)
    db.commit()
