from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
import re
from .auth import get_current_user, require_admin
from pydantic import BaseModel

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)

# Password strength validation
PASSWORD_REGEX = re.compile(r'^(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$')

class RoleUpdate(BaseModel):
    role: str

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not PASSWORD_REGEX.match(user.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters and contain a special character.")
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered.")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user 

@app.post("/auth/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token_data = {
        "sub": str(db_user.id),
        "username": db_user.username,
        "role": db_user.role
    }
    access_token = auth.create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"} 

@app.get("/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user 

@app.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.User).all()

@app.put("/users/{user_id}/role", response_model=schemas.UserResponse)
def change_user_role(user_id: int, role_update: RoleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted."} 