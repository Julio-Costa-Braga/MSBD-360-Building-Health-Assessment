import base64
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.photo import Photo
from app.models.room import Room
from app.schemas.photo import PhotoBulkCreate, PhotoCreate, PhotoRead

router = APIRouter(prefix="/rooms/{room_id}/photos", tags=["Photos"])

UPLOAD_DIR = "uploads/photos"


def _decode_base64(data: str) -> tuple[bytes, str]:
    """Decode base64 image data and return (bytes, extension)."""
    if "," in data:
        header, b64 = data.split(",", 1)
        ext_map = {
            "/": "jpg", "i": "png", "R": "gif", "U": "webp",
            "Q": "jpg", "k": "jpg",
        }
        ext = "jpg"
        for key, val in ext_map.items():
            if key in header:
                ext = val
                break
        if "png" in header:
            ext = "png"
        elif "gif" in header:
            ext = "gif"
        elif "webp" in header:
            ext = "webp"
    else:
        b64 = data
        ext = "jpg"
    return base64.b64decode(b64), ext


@router.post("", response_model=PhotoRead, status_code=201)
def upload_photo(
    room_id: int,
    data: PhotoCreate,
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    if data.photo_data:
        img_bytes, ext = _decode_base64(data.photo_data)
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(img_bytes)

    photo = Photo(
        room_id=room_id,
        file_path=filepath,
        caption=data.caption,
        photo_type=data.photo_type,
        photo_data=data.photo_data,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.post("/bulk", response_model=list[PhotoRead], status_code=201)
def upload_photos_bulk(
    room_id: int,
    data: PhotoBulkCreate,
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    created = []
    for pdata in data.photos:
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        if pdata.photo_data:
            img_bytes, ext = _decode_base64(pdata.photo_data)
            filename = f"{uuid.uuid4()}.{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(img_bytes)
        photo = Photo(
            room_id=room_id,
            file_path=filepath,
            caption=pdata.caption,
            photo_type=pdata.photo_type,
            photo_data=pdata.photo_data,
        )
        db.add(photo)
        created.append(photo)
    db.commit()
    for p in created:
        db.refresh(p)
    return created


@router.get("", response_model=list[PhotoRead])
def list_photos(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Cômodo não encontrado")
    return db.query(Photo).filter(Photo.room_id == room_id).order_by(Photo.taken_at.desc()).all()


@router.delete("/{photo_id}", status_code=204)
def delete_photo(room_id: int, photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.room_id == room_id).first()
    if not photo:
        raise HTTPException(404, "Foto não encontrada")
    if os.path.exists(photo.file_path):
        os.remove(photo.file_path)
    db.delete(photo)
    db.commit()
