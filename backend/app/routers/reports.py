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


@router.get("/isa")
def get_isa(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")

    rooms = db.query(Room).filter(Room.inspection_id == inspection_id).all()
    rooms_data = []
    for room in rooms:
        measurements = db.query(Measurement).filter(Measurement.room_id == room.id).all()
        photos = db.query(Photo).filter(Photo.room_id == room.id).all()
        rooms_data.append({
            "id": room.id,
            "name": room.name,
            "measurements": [
                {
                    "temperature": m.temperature,
                    "relative_humidity": m.relative_humidity,
                    "co2": m.co2,
                    "surface_temperature": m.surface_temperature,
                    "material_moisture": m.material_moisture,
                    "illuminance": m.illuminance,
                    "observations": m.observations,
                }
                for m in measurements
            ],
            "photos": [{"id": p.id} for p in photos],
        })

    result = calculator.calculate_inspection(rooms_data)

    inspection.overall_isa_score = result["overall_score"]
    db.commit()

    return result


@router.get("/pdf")
def download_pdf(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")

    rooms = db.query(Room).filter(Room.inspection_id == inspection_id).all()
    rooms_data = []
    for room in rooms:
        measurements = db.query(Measurement).filter(Measurement.room_id == room.id).all()
        photos = db.query(Photo).filter(Photo.room_id == room.id).all()
        rooms_data.append({
            "id": room.id,
            "name": room.name,
            "measurements": [
                {
                    "temperature": m.temperature,
                    "relative_humidity": m.relative_humidity,
                    "co2": m.co2,
                    "surface_temperature": m.surface_temperature,
                    "material_moisture": m.material_moisture,
                    "illuminance": m.illuminance,
                    "observations": m.observations,
                }
                for m in measurements
            ],
            "photos": [{"id": p.id} for p in photos],
        })

    isa_result = calculator.calculate_inspection(rooms_data)

    insp_dict = {
        "id": inspection.id,
        "client_name": inspection.client_name,
        "property_address": inspection.property_address,
        "inspector_name": inspection.inspector_name,
        "inspection_date": inspection.inspection_date.isoformat(),
    }

    pdf_bytes = generate_report(insp_dict, isa_result)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=msbd360-report-{inspection_id}.pdf"},
    )
