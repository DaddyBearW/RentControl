"""Create or update a local administrator account."""
import os
from app.database import Base, engine, SessionLocal
from app.models import User, Equipment
from app.core.config import settings
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    email = os.getenv("ADMIN_EMAIL") or settings.admin_email
    password = os.getenv("ADMIN_PASSWORD") or settings.admin_password
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, full_name="Администратор", password_hash=hash_password(password), role="admin")
        db.add(user)
    else:
        user.role = "admin"
        user.password_hash = hash_password(password)
    if db.query(Equipment).count() == 0:
        db.add_all([
            Equipment(name="Перфоратор Bosch GBH 2-26",category="Инструмент",description="Профессиональный перфоратор для строительных работ.",daily_price=850,quantity=4,image_url="https://images.unsplash.com/photo-1504148455328-c376907d081c?w=900"),
            Equipment(name="Лазерный нивелир DEWALT",category="Измерительное",description="Точный лазерный уровень для отделочных работ.",daily_price=1200,quantity=2,image_url="https://images.unsplash.com/photo-1581147036324-c1c89c2c8b5c?w=900"),
            Equipment(name="Генератор бензиновый 3 кВт",category="Электрооборудование",description="Компактный генератор для автономного электроснабжения.",daily_price=1900,quantity=3,image_url="https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=900")
        ])
    db.commit()
    print(f"Admin ready: {email}")
finally:
    db.close()
