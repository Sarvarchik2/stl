"""Pydantic Schemas - Cars."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class CarBase(BaseModel):
    brand: str
    make: str
    model: str
    year: int
    trim: Optional[str] = None
    body_type: Optional[str] = None
    mileage: Optional[int] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    fuel_type: Optional[str] = None
    engine: Optional[str] = None
    mpg_city: Optional[int] = None
    mpg_highway: Optional[int] = None
    status: str = "available"


class CarResponse(CarBase):
    id: UUID
    source: str
    source_url: Optional[str] = None
    source_price_usd: Decimal
    final_price_usd: Decimal  # Calculated field
    markup_percent: Optional[float] = 12.0
    dealer: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    photos: List[str] = []
    features: List[str] = []
    is_active: bool
    parsed_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarDetailResponse(CarResponse):
    """For staff - includes VIN."""
    vin: Optional[str] = None


class CarListParams(BaseModel):
    # Filters
    brand: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    price_from: Optional[Decimal] = None
    price_to: Optional[Decimal] = None
    body_type: Optional[str] = None
    exterior_color: Optional[str] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    is_active: Optional[bool] = True
    
    # Sorting
    sort_by: str = "created_at"  # price, year, mileage, created_at
    sort_order: str = "desc"  # asc, desc
    
    # Pagination
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    
    # Generic Search
    search: Optional[str] = None


class CarListResponse(BaseModel):
    items: List[CarResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CarCreate(CarBase):
    source_price_usd: Decimal
    source: Optional[str] = "manual"
    make: Optional[str] = None  # If not provided, will use brand
    is_active: Optional[bool] = True
    image_url: Optional[str] = None
    photos: List[str] = []
    features: List[str] = []
    vin: Optional[str] = None
    dealer: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    trim: Optional[str] = None
    body_type: Optional[str] = None
    mileage: Optional[int] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    fuel_type: Optional[str] = None
    engine: Optional[str] = None
    mpg_city: Optional[int] = None
    mpg_highway: Optional[int] = None
    source_price_usd: Optional[Decimal] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    photos: Optional[List[str]] = None
    features: Optional[List[str]] = None
    vin: Optional[str] = None
    dealer: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None


class PriceHistoryResponse(BaseModel):
    id: UUID
    price: Decimal
    recorded_at: datetime

    class Config:
        from_attributes = True


class CarMakesResponse(BaseModel):
    makes: List[str]
    total: int


class CarModelsResponse(BaseModel):
    models: List[str]
    total: int
