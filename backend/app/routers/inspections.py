from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inspection import Inspection
from app.schemas.inspection import InspectionCreate, InspectionListItem, InspectionRead, InspectionUpdate

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.get("", response_model=list[InspectionListItem])
def list_inspections(db: Session = Depends(get_db)):
    return db.query(Inspection).order_by(Inspection.created_at.desc()).all()


@router.post("", response_model=InspectionRead, status_code=201)
def create_inspection(data: InspectionCreate, db: Session = Depends(get_db)):
    inspection = Inspection(**data.model_dump())
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


@router.get("/{inspection_id}", response_model=InspectionRead)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")
    return inspection


@router.patch("/{inspection_id}", response_model=InspectionRead)
def update_inspection(inspection_id: int, data: InspectionUpdate, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inspection, key, value)
    db.commit()
    db.refresh(inspection)
    return inspection


@router.delete("/{inspection_id}", status_code=204)
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(404, "Inspeção não encontrada")
    db.delete(inspection)
    db.commit()
