from app.core.database import SessionLocal
from app.models.user import User

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "abc@gmail.com").first()
        if user:
            print(f"User found: ID={user.id}, Email={user.email}, Username={user.username}")
        else:
            print("User abc@gmail.com NOT found.")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
