from backend.app.database import SessionLocal
from backend.app.models import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"id={u.id}, email={u.email}, mobile={getattr(u, 'mobile_number', 'N/A')}, role={u.role}, active={getattr(u, 'is_active', 'N/A')}, verified={getattr(u, 'is_verified', 'N/A')}")
db.close()
