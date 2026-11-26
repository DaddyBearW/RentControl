from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import Rental, Equipment, User
from app.schemas import RentalCreate, RentalOut
from app.deps import current_user, require_roles
router = APIRouter(prefix="/api/rentals", tags=["Аренда"])

STATUS_LABELS = {"booked": "Забронирована", "active": "Выдана", "returned": "Возвращена", "overdue": "Просрочена", "cancelled": "Отменена"}
def serialize(r):
    return {"id":r.id,"customer_id":r.customer_id,"customer_name":r.customer.full_name,"equipment_id":r.equipment_id,"equipment_name":r.equipment.name,"start_date":r.start_date,"end_date":r.end_date,"total_price":r.total_price,"status":r.status,"returned_at":r.returned_at}

@router.post("", response_model=RentalOut, status_code=201)
def create_rental(data: RentalCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if data.start_date < date.today(): raise HTTPException(400, "Дата начала не может быть в прошлом")
    if data.end_date < data.start_date: raise HTTPException(400, "Дата окончания раньше даты начала")
    item = db.get(Equipment, data.equipment_id)
    if not item or not item.is_active: raise HTTPException(404, "Оборудование не найдено")
    overlapping = db.query(Rental).filter(Rental.equipment_id == item.id, Rental.status.in_(["booked", "active", "overdue"]), Rental.start_date <= data.end_date, Rental.end_date >= data.start_date).count()
    if overlapping >= item.quantity: raise HTTPException(409, "На выбранные даты нет свободного оборудования")
    days = (data.end_date - data.start_date).days + 1
    rental = Rental(customer_id=user.id, equipment_id=item.id, start_date=data.start_date, end_date=data.end_date, total_price=round(days * item.daily_price, 2), status="booked")
    db.add(rental); db.commit(); db.refresh(rental); return serialize(rental)

@router.get("", response_model=list[RentalOut])
def list_rentals(db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = db.query(Rental)
    if user.role == "customer": query = query.filter(Rental.customer_id == user.id)
    rows = query.order_by(Rental.created_at.desc()).all()
    today = date.today()
    changed = False
    for r in rows:
        if r.status in ("booked", "active") and r.end_date < today:
            r.status = "overdue"; changed = True
    if changed: db.commit()
    return [serialize(r) for r in rows]

@router.patch("/{rental_id}/issue", response_model=RentalOut)
def issue_rental(rental_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles("manager", "admin"))):
    r = db.get(Rental, rental_id)
    if not r: raise HTTPException(404, "Аренда не найдена")
    if r.status != "booked": raise HTTPException(409, "Выдать можно только забронированную аренду")
    r.status = "active"; db.commit(); db.refresh(r); return serialize(r)

@router.patch("/{rental_id}/return", response_model=RentalOut)
def return_rental(rental_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles("manager", "admin"))):
    r = db.get(Rental, rental_id)
    if not r: raise HTTPException(404, "Аренда не найдена")
    if r.status not in ("booked", "active", "overdue"): raise HTTPException(409, "Эту аренду нельзя вернуть")
    r.status = "returned"; r.returned_at = datetime.utcnow(); db.commit(); db.refresh(r); return serialize(r)
