from app.core.database import SessionLocal
from app.models.medicine import Medicine, Category
from app.models.user import User
from app.schemas.medicine import MedicineCreate

def test_medicine_creation():
    db = SessionLocal()
    
    try:
        # Test 1: Check if categories exist
        categories = db.query(Category).all()
        print(f"Available categories: {len(categories)}")
        for cat in categories:
            print(f"- ID: {cat.id}, Name: {cat.name}")
        
        # Test 2: Check if user exists
        users = db.query(User).all()
        print(f"Available users: {len(users)}")
        for user in users:
            print(f"- ID: {user.id}, Email: {user.email}, Role: {user.role}")
        
        # Test 3: Try to create a medicine directly
        medicine_data = {
            "name": "Test Medicine",
            "generic_name": "Test Generic",
            "description": "Test description",
            "manufacturer": "Test Manufacturer",
            "dosage_form": "tablet",
            "strength": "500mg",
            "prescription_required": False,
            "price": 10.0,
            "stock_quantity": 20,
            "min_stock_level": 10
        }
        
        print("\nTrying to create medicine...")
        medicine = Medicine(**medicine_data)
        db.add(medicine)
        db.commit()
        db.refresh(medicine)
        print(f"✅ Medicine created successfully! ID: {medicine.id}")
        
        # Test 4: Try with category
        if categories:
            medicine_data_with_category = medicine_data.copy()
            medicine_data_with_category["name"] = "Test Medicine with Category"
            medicine_data_with_category["category_id"] = categories[0].id
            
            print("\nTrying to create medicine with category...")
            medicine_with_category = Medicine(**medicine_data_with_category)
            db.add(medicine_with_category)
            db.commit()
            db.refresh(medicine_with_category)
            print(f"✅ Medicine with category created successfully! ID: {medicine_with_category.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_medicine_creation() 