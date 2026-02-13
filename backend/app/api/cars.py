"""Cars Catalog API routes."""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal
from uuid import UUID

from ..dependencies import DB, CurrentUser, StaffUser, ManagerUser, AdminUser, OptionalUser
from ..models.car import Car, PriceHistory
from ..models.enums import Role
from ..schemas.car import (
    CarResponse, CarDetailResponse, CarListResponse, 
    CarListParams, PriceHistoryResponse,
    CarMakesResponse, CarModelsResponse,
    CarCreate, CarUpdate
)
from ..services.pricing import get_final_price, get_markup_percent, calculate_final_price

router = APIRouter(prefix="/cars", tags=["Cars Catalog"])


@router.get("", response_model=CarListResponse)
async def list_cars(
    db: DB,
    params: CarListParams = Depends()
):
    """
    List cars with filtering, sorting and pagination.
    Prices returned are FINAL prices (including markup).
    """
    # Get current markup
    markup = await get_markup_percent(db)
    
    # Base query
    query = select(Car)
    
    # Filters
    if params.brand:
        query = query.where(Car.brand.ilike(f"%{params.brand}%"))
    if params.make:
        query = query.where(Car.make.ilike(f"%{params.make}%"))
    if params.model:
        query = query.where(Car.model.ilike(f"%{params.model}%"))
    if params.year_from:
        query = query.where(Car.year >= params.year_from)
    if params.year_to:
        query = query.where(Car.year <= params.year_to)
    if params.body_type:
        query = query.where(Car.body_type.ilike(f"%{params.body_type}%"))
    if params.exterior_color:
        query = query.where(Car.exterior_color.ilike(f"%{params.exterior_color}%"))
    if params.mileage_from:
        query = query.where(Car.mileage >= params.mileage_from)
    if params.mileage_to:
        query = query.where(Car.mileage <= params.mileage_to)
    if params.is_active is not None:
        query = query.where(Car.is_active == params.is_active)
    
    if params.search:
        s = f"%{params.search}%"
        query = query.where(
            (Car.brand.ilike(s)) |
            (Car.model.ilike(s)) |
            (Car.vin.ilike(s)) |
            (Car.external_id.ilike(s))
        )
        
    # Price filtering logic (reverse calculation from final price)
    # final = source * (1 + markup/100)  =>  source = final / (1 + markup/100)
    multiplier = 1 + (markup / 100)
    
    if params.price_from:
        source_min = params.price_from / multiplier
        query = query.where(Car.source_price_usd >= source_min)
    if params.price_to:
        source_max = params.price_to / multiplier
        query = query.where(Car.source_price_usd <= source_max)
    
    # Sorting
    if params.sort_by == "price":
        sort_col = Car.source_price_usd
    elif params.sort_by == "year":
        sort_col = Car.year
    elif params.sort_by == "mileage":
        sort_col = Car.mileage
    else:
        sort_col = Car.created_at
        
    if params.sort_order == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Pagination
    query = query.offset((params.page - 1) * params.per_page).limit(params.per_page)
    
    # Execute
    result = await db.execute(query)
    cars = result.scalars().all()
    
    # Transform to response (calculate final prices)
    items = []
    for car in cars:
        final_price = calculate_final_price(car.source_price_usd, markup)
        # Convert to dict and add calculated fields
        car_dict = {
            "id": car.id,
            "source": car.source,
            "source_url": car.source_url,
            "brand": car.brand,
            "make": car.make,
            "model": car.model,
            "year": car.year,
            "trim": car.trim,
            "body_type": car.body_type,
            "mileage": car.mileage,
            "exterior_color": car.exterior_color,
            "interior_color": car.interior_color,
            "transmission": car.transmission,
            "drivetrain": car.drivetrain,
            "fuel_type": car.fuel_type,
            "engine": car.engine,
            "mpg_city": car.mpg_city,
            "mpg_highway": car.mpg_highway,
            "source_price_usd": car.source_price_usd,
            "final_price_usd": final_price,
            "markup_percent": float(markup),
            "dealer": car.dealer,
            "location_city": car.location_city,
            "location_state": car.location_state,
            "location": car.location,
            "image_url": car.image_url,
            "photos": car.photos or [],
            "features": car.features or [],
            "status": car.status,
            "is_active": car.is_active,
            "parsed_at": car.parsed_at,
            "last_seen_at": car.last_seen_at,
        }
        car_resp = CarResponse(**car_dict)
        items.append(car_resp)
        
    return CarListResponse(
        items=items,
        total=total,
        page=params.page,
        per_page=params.per_page,
        pages=(total + params.per_page - 1) // params.per_page
    )


@router.get("/makes", response_model=CarMakesResponse)
async def list_makes(db: DB):
    """Get list of available car makes."""
    query = select(Car.make).where(Car.is_active == True).distinct().order_by(Car.make)
    result = await db.execute(query)
    makes = result.scalars().all()
    return CarMakesResponse(makes=makes, total=len(makes))


@router.get("/models", response_model=CarModelsResponse)
async def list_models(db: DB, make: str):
    """Get list of available models for a make."""
    query = select(Car.model).where(
        (Car.is_active == True) & 
        (Car.make.ilike(make))
    ).distinct().order_by(Car.model)
    result = await db.execute(query)
    models = result.scalars().all()
    return CarModelsResponse(models=models, total=len(models))


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: str, 
    db: DB,
    current_user: OptionalUser
):
    """
    Get car details.
    VIN is hidden for clients, visible for staff.
    """
    # Try to parse UUID
    try:
        from uuid import UUID
        uuid_obj = UUID(car_id)
        query = select(Car).where(Car.id == uuid_obj)
    except ValueError:
        # Try external_id if not UUID
        query = select(Car).where(Car.external_id == car_id)
        
    result = await db.execute(query)
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        
    # Calculate price
    final_price, markup = await get_final_price(db, car.source_price_usd)
    
    # Check permissions for detailed view (VIN)
    is_staff = False
    if current_user and current_user.role in [Role.OPERATOR, Role.SUPERVISOR, Role.MANAGER, Role.ADMIN, Role.OWNER]:
        is_staff = True
        
    if is_staff:
        resp = CarDetailResponse.model_validate(car)
    else:
        resp = CarResponse.model_validate(car)
        
    resp.final_price_usd = final_price
    resp.markup_percent = float(markup)
    
    return resp


@router.get("/{car_id}/price-history", response_model=List[PriceHistoryResponse])
async def get_car_price_history(
    car_id: str,
    staff_user: StaffUser,
    db: DB
):
    """Get price history for a car (Staff only)."""
    # Resolve ID
    try:
        from uuid import UUID
        uuid_obj = UUID(car_id)
        query = select(Car).where(Car.id == uuid_obj)
    except ValueError:
        query = select(Car).where(Car.external_id == car_id)
        
    result = await db.execute(query)
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        
    history_query = select(PriceHistory).where(
        PriceHistory.car_id == car.id
    ).order_by(desc(PriceHistory.recorded_at))
    
    result = await db.execute(history_query)
    return result.scalars().all()


@router.post("", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    car_in: CarCreate,
    current_user: ManagerUser,
    db: DB
):
    """Create a new car (Manager+)."""
    # Calculate initial final price
    markup = await get_markup_percent(db)
    final_price = calculate_final_price(car_in.source_price_usd, markup)
    
    # Use brand as make if not provided
    make = car_in.make or car_in.brand
    
    car = Car(
        **car_in.model_dump(exclude={"make"}),
        make=make,
        final_price_usd=final_price
    )
    
    db.add(car)
    await db.commit()
    await db.refresh(car)
    
    # Add initial price history
    history = PriceHistory(car_id=car.id, price=car.source_price_usd)
    db.add(history)
    await db.commit()
    
    return car


@router.patch("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: UUID,
    car_in: CarUpdate,
    current_user: ManagerUser,
    db: DB
):
    """Update car details (Manager+)."""
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        
    update_data = car_in.model_dump(exclude_unset=True)
    
    # If price changed, update final price and history
    if "source_price_usd" in update_data:
        markup = await get_markup_percent(db)
        car.final_price_usd = calculate_final_price(update_data["source_price_usd"], markup)
        
        # Add price history
        history = PriceHistory(car_id=car.id, price=update_data["source_price_usd"])
        db.add(history)
    
    for field, value in update_data.items():
        setattr(car, field, value)
        
    await db.commit()
    await db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: UUID,
    current_user: ManagerUser,
    db: DB
):
    """Delete a car (Manager+)."""
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        
    await db.delete(car)
    await db.commit()
    return None
