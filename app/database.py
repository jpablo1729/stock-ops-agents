from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings
import random

# Create the database engine using the URL from settings.
# pool_pre_ping=True verifies the connection is alive before using it.
engine = create_engine(
    settings.database_url.get_secret_value() if hasattr(settings.database_url, 'get_secret_value') else settings.database_url,
    pool_pre_ping=True,
)

# Create a session factory for database transactions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()

class Product(Base):
    """Represents a product in the store's inventory."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)

class ChatSession(Base):
    """Stores the conversation history for a user's chat session."""
    __tablename__ = "chat_sessions"

    session_id = Column(String(100), primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    messages_json = Column(Text, nullable=False, default="[]")
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

def get_db():
    """Dependency generator to yield a database session and ensure it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates tables and populates the database with initial product data."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Check if the products table is empty to avoid duplicating data on restart.
        if db.query(Product).count() == 0:
            # Define base categories and their respective items to generate varied products
            categories = {
                "Microcontrollers": ["ESP32-S3 DevKit", "Arduino Mega", "Raspberry Pi Pico", "STM32 Nucleo"],
                "Sensors": ["LiDAR Sensor", "Temperature Probe", "Ultrasonic Sensor", "PIR Motion Sensor",
                            "Humidity Sensor"],
                "Actuators": ["Servo Motor", "Stepper Motor", "Solenoid Valve", "Linear Actuator"],
                "Power": ["LiPo Battery 3.7V", "Power Supply 12V 5A", "DC-DC Buck Converter", "Solar Panel 6V"],
                "Tools": ["Soldering Iron", "Multimeter", "Oscilloscope", "Wire Stripper", "Heat Gun"]
            }

            products_to_add = []

            # Generate 100 products using a loop
            for i in range(1, 101):
                # Pick a random category
                category = random.choice(list(categories.keys()))
                # Pick a random base name from that category
                base_name = random.choice(categories[category])

                # Create unique name and SKU
                name = f"{base_name} - Model {i:03d}"
                sku = f"SKU-{i:03d}"

                # Generate random price and stock (some will have stock 0 to test logic)
                price = round(random.uniform(5.0, 500.0), 2)
                stock = random.randint(0, 150)

                products_to_add.append(
                    Product(
                        sku=sku,
                        name=name,
                        category=category,
                        price=price,
                        stock=stock
                    )
                )

            # Add all products to the database at once
            db.add_all(products_to_add)
            db.commit()
            print(f"Successfully inserted {len(products_to_add)} products into the database.")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()