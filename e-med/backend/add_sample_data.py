from app.core.database import SessionLocal
from app.models.medicine import Category
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def add_sample_data():
    db = SessionLocal()
    
    try:
        # Add sample categories
        categories = [
            Category(name="Pain Relief", description="Medicines for pain management"),
            Category(name="Fever & Cold", description="Medicines for fever and cold"),
            Category(name="Antibiotics", description="Antibiotic medications"),
            Category(name="Vitamins", description="Vitamin supplements"),
            Category(name="First Aid", description="First aid supplies")
        ]
        
        for category in categories:
            existing = db.query(Category).filter(Category.name == category.name).first()
            if not existing:
                db.add(category)
                print(f"Added category: {category.name}")
        
        # Add a pharmacy admin user if not exists
        admin_user = db.query(User).filter(User.email == "pharmacy@example.com").first()
        if not admin_user:
            admin_user = User(
                email="pharmacy@example.com",
                phone="1234567890",
                full_name="Pharmacy Admin",
                hashed_password=get_password_hash("Admin@123"),
                role=UserRole.PHARMACY_ADMIN,
                pharmacy_name="MediDash Pharmacy",
                pharmacy_address="123 Main St",
                license_number="PH123456"
            )
            db.add(admin_user)
            print("Added pharmacy admin user")
        
        db.commit()
        print("Sample data added successfully!")
        
        # Show existing categories
        categories = db.query(Category).all()
        print(f"\nAvailable categories:")
        for cat in categories:
            print(f"- ID: {cat.id}, Name: {cat.name}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data() 