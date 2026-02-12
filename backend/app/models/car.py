"""SQLAlchemy Models - Cars (integrating with existing parser data)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Car(Base):
    """Car model - catalog from cars.com."""
    __tablename__ = "cars_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source info
    source = Column(String(50), default="cars.com", nullable=False)
    source_url = Column(Text, nullable=True)
    external_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Car details
    brand = Column(String(100), nullable=False, index=True)  # Alias for make
    make = Column(String(100), nullable=False, index=True)  # Same as brand
    model = Column(String(200), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    trim = Column(String(200), nullable=True)
    body_type = Column(String(100), nullable=True)
    
    # Specs
    mileage = Column(Integer, nullable=True)
    exterior_color = Column(String(100), nullable=True)
    interior_color = Column(String(100), nullable=True)
    transmission = Column(String(100), nullable=True)
    drivetrain = Column(String(50), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    engine = Column(String(200), nullable=True)
    mpg_city = Column(Integer, nullable=True)
    mpg_highway = Column(Integer, nullable=True)
    
    # VIN - hidden from clients
    vin = Column(String(17), nullable=True, index=True)
    
    # Pricing
    source_price_usd = Column(Numeric(12, 2), nullable=False)
    final_price_usd = Column(Numeric(12, 2), nullable=False)  # source_price + markup (12%)
    
    # Location
    dealer = Column(String(255), nullable=True)
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(10), nullable=True)
    location = Column(String(255), nullable=True)  # Legacy field
    
    # Media
    image_url = Column(Text, nullable=True)
    photos = Column(JSON, default=list)
    
    # Features
    features = Column(JSON, default=list)
    
    # Status
    status = Column(String(50), default="available", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    parsed_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    source_updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def markup_percent(self) -> float:
        """Return the fixed markup percentage."""
        return 12.0

    # Relationships
    applications = relationship("Application", back_populates="car")
    price_history = relationship("PriceHistory", back_populates="car", foreign_keys="PriceHistory.car_id")


class PriceHistory(Base):
    """Price history for tracking price changes."""
    __tablename__ = "cars_price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey("cars_catalog.id"), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    car = relationship("Car", back_populates="price_history")
