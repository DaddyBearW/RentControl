from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Equipment, Rental
from app.schemas import UserOut, UserRoleUpdate
from app.deps import require_roles
router = APIRouter(prefix="/api/admin", tags=["Администрирование"])

@router.get("/users", response_model=list[UserOut])
def users(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return db.query(User).order_by(User.id).all()

@router.patch("/users/{user_id}/role", response_model=UserOut)
def change_role(user_id: int, data: UserRoleUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    if data.role not in ("customer", "manager", "admin"): raise HTTPException(400, "Недопустимая роль")
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "Пользователь не найден")
    user.role = data.role; db.commit(); db.refresh(user); return user

@router.get("/stats")
def stats(db: Session = Depends(get_db), _: User = Depends(require_roles("manager", "admin"))):
    return {"equipment_count": db.query(Equipment).filter(Equipment.is_active == True).count(), "rental_count": db.query(Rental).count(), "active_rentals": db.query(Rental).filter(Rental.status == "active").count(), "overdue_rentals": db.query(Rental).filter(Rental.status == "overdue").count(), "users_count": db.query(User).count()}
