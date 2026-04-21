from fastapi import FastAPI, Query, Depends, Request, HTTPException, status 
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .database import get_db, engine, Base
from .models import Profile 
from .parser import parse_natural_language 

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Clean up resources
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# --- CUSTOM ERROR HANDLING ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": "Invalid parameter type"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Server failure"},
    )

# --- ENDPOINTS ---

@app.get("/api/profiles")
async def get_profiles(
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    country_id: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_gender_probability: Optional[float] = None,
    min_country_probability: Optional[float] = None,
    sort_by: str = "created_at",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    # Validation for Sort fields
    if sort_by not in ["age", "created_at", "gender_probability"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query parameters")

    stmt = select(Profile)
    filters = []

    if gender: filters.append(Profile.gender == gender.lower())
    if age_group: filters.append(Profile.age_group == age_group.lower())
    if country_id: filters.append(Profile.country_id == country_id.upper())
    if min_age is not None: filters.append(Profile.age >= min_age)
    if max_age is not None: filters.append(Profile.age <= max_age)
    if min_gender_probability: filters.append(Profile.gender_probability >= min_gender_probability)
    if min_country_probability: filters.append(Profile.country_probability >= min_country_probability)

    if filters: stmt = stmt.where(and_(*filters))

    # Apply Sorting
    sort_attr = getattr(Profile, sort_by)
    stmt = stmt.order_by(sort_attr.desc() if order == "desc" else sort_attr.asc())

    # Pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)
    
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": result.scalars().all()
    }

@app.get("/api/profiles/search")
async def search_profiles(
    q: Optional[str] = Query(None), 
    page: int = 1, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db)
):
    if not q or not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing or empty parameter")

    interpreted_filters = parse_natural_language(q)
    
    if not interpreted_filters:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to interpret query")
    
    return await get_profiles(**interpreted_filters, page=page, limit=limit, db=db)