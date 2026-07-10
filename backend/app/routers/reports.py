from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import Inspection
from app.models.measurement import Measurement
from app.models.photo import Photo
from app.models.room import Room
from app.services.isa_calculator import ISACalculator
from app.services.report_generator import generate_report

router = APIRouter(prefix="/inspections/{inspection_id}/reports", tags=["Reports"])
calculator = ISACalculator()


def _build_rooms_data(inspection_id: int, db: Session, include_photos: bool = False) -> list[dict]:
    rooms = db.query(Room).filter(Room.inspection_id == inspection_id).all()
    rooms_data = []
    for room in rooms:
        measurements = db.query(Measurement).filter(Measurement.room_id == room.id).all()
        photos_qs = db.query(Photo).filter(Photo.room_id == room.id).all()
        photos = []
        for p in photos_qs:
            photo_entry = {"id": p.id}
            if include_photos:
                photo_entry["photo_data"] = p.photo_data
                photo_entry["photo_type"] = p.photo_type
                photo_entry["caption"] = p.caption
            photos.append(photo_entry)
        rooms_data.append({
            "id": room.id,
            "name": room.name,
            "room_type": room.room_type,
            "measurements": [
                {
                    "temperature": m.temperature,
                    "relative_humidity": m.relative_humidity,
                    "co2": m.co2,
                    "surface_temperature": m.surface_temperature,
                    "material_moisture": m.material_moisture,
                    "illuminance": m.illuminance,
                    "observations": m.observations,
                    "sub_location": m.sub_location,
                }
                for m in measurements
            ],
            "photos": photos,
        })
    return rooms_data


@router.get("/isa")
def get_isa(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")

    rooms_data = _build_rooms_data(inspection_id, db)
    result = calculator.calculate_inspection(rooms_data)

    inspection.overall_isa_score = result["overall_score"]
    db.commit()

    return result


@router.get("/isa-by-type")
def get_isa_by_type(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")

    rooms_data = _build_rooms_data(inspection_id, db)
    result = calculator.calculate_by_room_type(rooms_data)
    return result


@router.get("/pdf")
def download_pdf(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")

    rooms_data = _build_rooms_data(inspection_id, db, include_photos=True)
    isa_result = calculator.calculate_inspection(rooms_data)

    insp_date = inspection.inspection_date
    if hasattr(insp_date, "strftime"):
        formatted_date = insp_date.strftime("%d/%m/%Y")
    else:
        formatted_date = str(insp_date)

    insp_dict = {
        "id": inspection.id,
        "client_name": inspection.client_name,
        "property_address": inspection.property_address,
        "inspector_name": inspection.inspector_name,
        "inspection_date": formatted_date,
    }

    pdf_bytes = generate_report(insp_dict, isa_result, rooms_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=msbd360-report-{inspection_id}.pdf"},
    )
