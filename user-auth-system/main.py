from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
import re
from .auth import get_current_user, require_admin
from pydantic import BaseModel
from .utils import RateLimiter, blacklist_token, forgot_password_limiter, login_limiter, register_limiter, general_api_limiter
from pydantic import EmailStr
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi.responses import JSONResponse
from fastapi.requests import Request as FastAPIRequest
from fastapi import HTTPException as FastAPIHTTPException
import logging

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

refresh_limiter = RateLimiter(5, 60)  # 5 requests per 60 seconds per IP

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
def register(user: schemas.UserCreate, db: Session = Depends(get_db), request: Request = None):
    ip = request.client.host if request and request.client else "unknown"
    register_limiter.check(ip, "/auth/register")
    general_api_limiter.check(ip, "/auth/register")
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
def login(user: schemas.UserLogin, db: Session = Depends(get_db), request: Request = None):
    ip = request.client.host if request and request.client else "unknown"
    login_limiter.check(ip, "/auth/login")
    general_api_limiter.check(ip, "/auth/login")
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.get_hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token_data = {
        "sub": str(db_user.id),
        "username": db_user.username,
        "role": db_user.get_role
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

@app.post("/auth/refresh", response_model=schemas.Token)
def refresh_token(request: Request, current_user: models.User = Depends(get_current_user)):
    ip = request.client.host if request.client else "unknown"
    refresh_limiter.check(ip, "/auth/refresh")
    token_data = {
        "sub": str(current_user.id),
        "username": current_user.username,
        "role": current_user.get_role
    }
    access_token = auth.create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"} 

@app.post("/auth/logout")
def logout(request: Request, current_user: models.User = Depends(get_current_user)):
    # Extract token from Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="No token found in Authorization header.")
    token = auth_header.split(" ", 1)[1]
    blacklist_token(token)
    return {"detail": "Successfully logged out."} 

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@app.post("/auth/forgot-password")
def forgot_password(request: Request, body: ForgotPasswordRequest):
    ip = request.client.host if request.client else "unknown"
    forgot_password_limiter.check(ip, "/auth/forgot-password")
    # Here you would normally send a password reset email or token
    return {"detail": f"If an account with {body.email} exists, a password reset link will be sent."} 

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try a simple DB query
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}, 500 

# For general API rate limiting, add a dependency to all endpoints (except /health)
def general_rate_limit_dependency(request: Request):
    ip = request.client.host if request and request.client else "unknown"
    general_api_limiter.check(ip, request.url.path)

# Add general_api_limiter as a dependency to all endpoints except /health
for route in app.routes:
    if hasattr(route, "path") and route.path != "/health":
        if hasattr(route, "dependant"):
            route.dependant.dependencies.append(Depends(general_rate_limit_dependency)) 

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware) 

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: FastAPIRequest, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: FastAPIRequest, exc: Exception):
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    ) 