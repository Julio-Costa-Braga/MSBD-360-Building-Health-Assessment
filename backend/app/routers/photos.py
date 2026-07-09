import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.photo import Photo
from app.models.room import Room
from app.schemas.photo import PhotoRead

router = APIRouter(prefix="/rooms/{room_id}/photos", tags=["Photos"])

UPLOAD_DIR = "uploads/photos"


@router.post("", response_model=PhotoRead, status_code=201)
async def upload_photo(
    room_id: int,
    file: UploadFile = File(...),
    caption: str = Form(""),
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or ".jpg")[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    photo = Photo(room_id=room_id, file_path=filepath, caption=caption)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("", response_model=list[PhotoRead])
def list_photos(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")
    return db.query(Photo).filter(Photo.room_id == room_id).all()


@router.delete("/{photo_id}", status_code=204)
def delete_photo(room_id: int, photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.room_id == room_id).first()
    if not photo:
        raise HTTPException(404, "Foto não encontrada")
    if os.path.exists(photo.file_path):
        os.remove(photo.file_path)
    db.delete(photo)
    db.commit()
