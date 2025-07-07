from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, select, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import date as dt_date, datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator
import random

DATABASE_URL = "sqlite:///./expenses.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Other"]

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, default=dt_date.today)

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None
    date: Optional[dt_date] = None

    @validator('category')
    def category_must_be_valid(cls, v):
        if v not in CATEGORIES:
            raise ValueError(f"Category must be one of {CATEGORIES}")
        return v

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[dt_date] = None

    @validator('category')
    def category_must_be_valid(cls, v):
        if v is not None and v not in CATEGORIES:
            raise ValueError(f"Category must be one of {CATEGORIES}")
        return v

class ExpenseOut(BaseModel):
    id: int
    amount: float
    category: str
    description: Optional[str]
    date: dt_date
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Expense).count() == 0:
        # Add sample data
        for _ in range(10):
            db.add(Expense(
                amount=round(random.uniform(5, 100), 2),
                category=random.choice(CATEGORIES),
                description="Sample expense",
                date=dt_date(2025, 7, random.randint(1, 28))
            ))
        db.commit()
    db.close()

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Expense Tracker API"}

@app.get("/expenses", response_model=List[ExpenseOut])
def get_expenses(
    start_date: Optional[dt_date] = None,
    end_date: Optional[dt_date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Expense)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    return query.order_by(Expense.date.desc()).all()

@app.post("/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(**expense.dict(exclude_unset=True))
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.put("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for key, value in expense.dict(exclude_unset=True).items():
        setattr(db_expense, key, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(db_expense)
    db.commit()
    return

@app.get("/expenses/category/{category}", response_model=List[ExpenseOut])
def get_expenses_by_category(category: str, db: Session = Depends(get_db)):
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Category must be one of {CATEGORIES}")
    return db.query(Expense).filter(Expense.category == category).order_by(Expense.date.desc()).all()

@app.get("/expenses/total")
def get_total_expenses(db: Session = Depends(get_db)):
    total = db.query(func.sum(Expense.amount)).scalar() or 0
    breakdown = db.query(Expense.category, func.sum(Expense.amount)).group_by(Expense.category).all()
    return {
        "total": round(total, 2),
        "breakdown": {cat: round(amt, 2) for cat, amt in breakdown}
    } 