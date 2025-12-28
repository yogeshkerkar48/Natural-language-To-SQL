from app.core.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

def delete_user():
    db = SessionLocal()
    try:
        # Delete abc user
        user = db.query(User).filter(User.email == "abc@gmail.com").first()
        if user:
            print(f"Deleting user {user.email} (ID: {user.id})")
            db.delete(user)
            db.commit()
            print("User deleted.")
        else:
            print("User abc@gmail.com not found.")
            
        # Delete test_script user
        user2 = db.query(User).filter(User.email == "test_script@gmail.com").first()
        if user2:
             db.delete(user2)
             db.commit()
             print("Test script user deleted.")

    except Exception as e:
        print(f"Error deleting user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_user()
