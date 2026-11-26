from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Equipment, User
from app.schemas import EquipmentCreate, EquipmentOut
from app.deps import current_user, require_roles
router = APIRouter(prefix="/api/equipment", tags=["Оборудование"])

@router.get("", response_model=list[EquipmentOut])
def list_equipment(q: str = "", category: str = "", db: Session = Depends(get_db)):
    query = db.query(Equipment).filter(Equipment.is_active == True)
    if q: query = query.filter(Equipment.name.ilike(f"%{q}%"))
    if category: query = query.filter(Equipment.category == category)
    return query.order_by(Equipment.id.desc()).all()

@router.get("/{equipment_id}", response_model=EquipmentOut)
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    item = db.get(Equipment, equipment_id)
    if not item or not item.is_active: raise HTTPException(404, "Оборудование не найдено")
    return item

@router.post("", response_model=EquipmentOut, status_code=201)
def create_equipment(data: EquipmentCreate, db: Session = Depends(get_db), user: User = Depends(require_roles("manager", "admin"))):
    item = Equipment(**data.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.patch("/{equipment_id}", response_model=EquipmentOut)
def update_equipment(equipment_id: int, data: EquipmentCreate, db: Session = Depends(get_db), user: User = Depends(require_roles("manager", "admin"))):
    item = db.get(Equipment, equipment_id)
    if not item: raise HTTPException(404, "Оборудование не найдено")
    for key, value in data.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/{equipment_id}", status_code=204)
def deactivate_equipment(equipment_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles("admin"))):
    item = db.get(Equipment, equipment_id)
    if not item: raise HTTPException(404, "Оборудование не найдено")
    item.is_active = False; db.commit()
