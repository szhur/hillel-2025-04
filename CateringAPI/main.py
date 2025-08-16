from __future__ import annotations

import os
import datetime as dt
from typing import Any, Dict, List, Optional

import bcrypt
import jwt
import psycopg
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, ValidationError

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "60"))

# ----------------------------------------------------------------------------
# ORM (yours, slightly enhanced to return dicts)
# ----------------------------------------------------------------------------
class BaseModelORM:
    table_name = None

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    # helper to map rows to dicts
    @staticmethod
    def _to_dicts(description, rows):
        cols = [c.name if hasattr(c, "name") else c[0] for c in description]
        return [dict(zip(cols, r)) for r in rows]

    def get_all(self):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table_name} ORDER BY id ASC")
            rows = cur.fetchall()
            return self._to_dicts(cur.description, rows)

    def filter(self, **kwargs):
        if not kwargs:
            return self.get_all()
        conditions = " AND ".join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values())
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table_name} WHERE {conditions}", values)
            rows = cur.fetchall()
            return self._to_dicts(cur.description, rows)

    def delete(self, **kwargs):
        if not kwargs:
            raise ValueError("delete() requires at least one condition")
        conditions = " AND ".join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values())
        with self.conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.table_name} WHERE {conditions}", values)
        self.conn.commit()

    def create(self, **kwargs):
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["%s"] * len(kwargs))
        values = tuple(kwargs.values())
        with self.conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING *",
                values,
            )
            row = cur.fetchone()
            self.conn.commit()
            return self._to_dicts(cur.description, [row])[0]

    def update(self, item_id, **kwargs):
        if not kwargs:
            raise ValueError("No fields to update")
        set_clause = ", ".join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values()) + (item_id,)
        with self.conn.cursor() as cur:
            cur.execute(
                f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s RETURNING *",
                values,
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail=f"{self.table_name[:-1].capitalize()} not found")
            self.conn.commit()
            return self._to_dicts(cur.description, [row])[0]


class UserORM(BaseModelORM):
    table_name = "users"


class DishORM(BaseModelORM):
    table_name = "dishes"


class OrderORM(BaseModelORM):
    table_name = "orders"


class OrderItemORM(BaseModelORM):
    table_name = "order_items"


# ----------------------------------------------------------------------------
# DB bootstrap (CREATE TABLE IF NOT EXISTS)
# ----------------------------------------------------------------------------
DDL = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'CUSTOMER',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS dishes (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        status TEXT NOT NULL DEFAULT 'DRAFT', -- DRAFT, PLACED, CANCELLED, COMPLETED
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
        dish_id INTEGER NOT NULL REFERENCES dishes(id),
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
]


# ----------------------------------------------------------------------------
# Auth helpers
# ----------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


def jwt_encode(payload: dict, ttl_minutes: int = ACCESS_TTL_MIN) -> str:
    now = dt.datetime.utcnow()
    payload = {**payload, "iat": now, "exp": now + dt.timedelta(minutes=ttl_minutes)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def jwt_decode(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def pair_user_from_token(token: str) -> int:
    data = jwt_decode(token)
    if data.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return int(data["sub"])  # type: ignore


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ----------------------------------------------------------------------------
# FastAPI app and dependencies
# ----------------------------------------------------------------------------
app = FastAPI(title="Catering API", version="1.0.0")


def get_conn():
    with psycopg.connect(DATABASE_URL, autocommit=False) as conn:
        # ensure schema exists once per connection (cheap)
        with conn.cursor() as cur:
            for stmt in DDL:
                cur.execute(stmt)
        conn.commit()
        yield conn


def get_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        return pair_user_from_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ----------------------------------------------------------------------------
# Pydantic models (requests / responses)
# ----------------------------------------------------------------------------
class RegisterIn(BaseModel):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    created_at: dt.datetime

class DishIn(BaseModel):
    name: str
    price: float = Field(ge=0)
    is_active: bool = True

class DishOut(BaseModel):
    id: int
    name: str
    price: float
    is_active: bool
    created_at: dt.datetime

class OrderCreateIn(BaseModel):
    # empty; created for current user
    pass

class AddItemIn(BaseModel):
    dish_id: int
    quantity: int = Field(gt=0)

class OrderItemOut(BaseModel):
    id: int
    order_id: int
    dish_id: int
    quantity: int
    unit_price: float
    created_at: dt.datetime

class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    created_at: dt.datetime
    items: List[OrderItemOut] = []
    total: float = 0.0

class OrderStatusUpdateIn(BaseModel):
    status: str  # DRAFT, PLACED, CANCELLED, COMPLETED


# ----------------------------------------------------------------------------
# Auth endpoints
# ----------------------------------------------------------------------------
@app.post("/auth/register", response_model=UserOut)
def register(payload: RegisterIn, conn: psycopg.Connection = Depends(get_conn)):
    users = UserORM(conn)
    existing = users.filter(username=payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hash_password(payload.password)
    row = users.create(
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        password_hash=hashed,
        role="CUSTOMER",
    )
    return row  # converted by ORM


@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, conn: psycopg.Connection = Depends(get_conn)):
    users = UserORM(conn)
    found = users.filter(username=payload.username)
    if not found:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = found[0]
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt_encode({"sub": str(user["id"]), "type": "access"}, ttl_minutes=ACCESS_TTL_MIN)
    return {"access_token": token, "token_type": "bearer"}


# ----------------------------------------------------------------------------
# Dish endpoints (CRUD)
# ----------------------------------------------------------------------------
@app.get("/dishes", response_model=List[DishOut])
def list_dishes(conn: psycopg.Connection = Depends(get_conn)):
    dishes = DishORM(conn)
    return dishes.get_all()


@app.post("/dishes", response_model=DishOut)
def create_dish(payload: DishIn, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    # In real life, check role ADMIN; for now allow any authenticated user
    dishes = DishORM(conn)
    return dishes.create(name=payload.name, price=payload.price, is_active=payload.is_active)


@app.get("/dishes/{dish_id}", response_model=DishOut)
def get_dish(dish_id: int, conn: psycopg.Connection = Depends(get_conn)):
    dishes = DishORM(conn)
    rows = dishes.filter(id=dish_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Dish not found")
    return rows[0]


@app.put("/dishes/{dish_id}", response_model=DishOut)
def update_dish(dish_id: int, payload: DishIn, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    dishes = DishORM(conn)
    return dishes.update(dish_id, name=payload.name, price=payload.price, is_active=payload.is_active)


@app.delete("/dishes/{dish_id}")
def delete_dish(dish_id: int, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    dishes = DishORM(conn)
    existing = dishes.filter(id=dish_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Dish not found")
    dishes.delete(id=dish_id)
    return {"ok": True}


# ----------------------------------------------------------------------------
# Orders + items
# ----------------------------------------------------------------------------
@app.post("/orders", response_model=OrderOut)
def create_order(user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    orders = OrderORM(conn)
    row = orders.create(user_id=user_id, status="DRAFT")
    return _order_with_items(row["id"], conn)


@app.get("/orders", response_model=List[OrderOut])
def list_my_orders(user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    orders = OrderORM(conn)
    rows = orders.filter(user_id=user_id)
    return [_order_with_items(r["id"], conn) for r in rows]


@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    _ensure_order_owner(order_id, user_id, conn)
    return _order_with_items(order_id, conn)


@app.post("/orders/{order_id}/items", response_model=OrderOut)
def add_item(order_id: int, payload: AddItemIn, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    _ensure_order_owner(order_id, user_id, conn)
    _ensure_order_status(order_id, conn, allowed={"DRAFT"})
    dishes = DishORM(conn)
    drows = dishes.filter(id=payload.dish_id)
    if not drows:
        raise HTTPException(status_code=404, detail="Dish not found")
    price = float(drows[0]["price"])  # capture current price
    items = OrderItemORM(conn)
    items.create(order_id=order_id, dish_id=payload.dish_id, quantity=payload.quantity, unit_price=price)
    return _order_with_items(order_id, conn)


@app.delete("/orders/{order_id}/items/{item_id}", response_model=OrderOut)
def remove_item(order_id: int, item_id: int, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    _ensure_order_owner(order_id, user_id, conn)
    _ensure_order_status(order_id, conn, allowed={"DRAFT"})
    items = OrderItemORM(conn)
    found = items.filter(id=item_id, order_id=order_id)
    if not found:
        raise HTTPException(status_code=404, detail="Item not found")
    items.delete(id=item_id)
    return _order_with_items(order_id, conn)


@app.put("/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, payload: OrderStatusUpdateIn, user_id: int = Depends(get_user_id), conn: psycopg.Connection = Depends(get_conn)):
    _ensure_order_owner(order_id, user_id, conn)
    allowed = {"DRAFT", "PLACED", "CANCELLED", "COMPLETED"}
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(allowed)}")
    orders = OrderORM(conn)
    orders.update(order_id, status=payload.status)
    return _order_with_items(order_id, conn)


# ----------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------

def _ensure_order_owner(order_id: int, user_id: int, conn: psycopg.Connection):
    orders = OrderORM(conn)
    rows = orders.filter(id=order_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Order not found")
    if rows[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not your order")


def _ensure_order_status(order_id: int, conn: psycopg.Connection, allowed: set[str]):
    orders = OrderORM(conn)
    rows = orders.filter(id=order_id)
    status_val = rows[0]["status"]
    if status_val not in allowed:
        raise HTTPException(status_code=400, detail=f"Operation allowed only in statuses: {sorted(allowed)}")


def _order_with_items(order_id: int, conn: psycopg.Connection) -> OrderOut:
    orders = OrderORM(conn)
    items = OrderItemORM(conn)
    orow = orders.filter(id=order_id)
    if not orow:
        raise HTTPException(status_code=404, detail="Order not found")
    orow = orow[0]
    irows = items.filter(order_id=order_id)
    total = sum(float(i["unit_price"]) * i["quantity"] for i in irows)
    return OrderOut(
        id=orow["id"],
        user_id=orow["user_id"],
        status=orow["status"],
        created_at=orow["created_at"],
        items=[OrderItemOut(**i) for i in irows],
        total=round(total, 2),
    )


# ----------------------------------------------------------------------------
# Health check + root
# ----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"service": "catering-api", "status": "ok"}