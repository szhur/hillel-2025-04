from dataclasses import dataclass
from pprint import pprint as print

import psycopg

connection_payload = {
    "dbname" : "catering",
    "user": "postgres",
    "password": "Thntddbghtfk1996",
    "host": "localhost",
    "port": 5432
}

class DatabaseConnection:
    def __enter__(self):
        self.conn = psycopg.connect(**connection_payload)
        self.cur = self.conn.cursor()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()

        self.cur.close()
        self.conn.close()

    def query(self, sql : str, params : tuple | None = None):
        self.cur.execute(sql, params or ())
        return self.cur.fetchall()

@dataclass
class User:
    name: str 
    phone: str
    role: str
    id: int | None = None

    @classmethod
    def all(cls) -> list["User"]:
        with DatabaseConnection() as db:
            rows = db.query("SELECT name, phone, role, id FROM users")
            return [cls(*row) for row in rows]
        
    @classmethod
    def filter(cls, **filters) -> list["User"]:
        keys = filters.keys()

        condition = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters[key] for key in keys)

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT name, phone, role, id FROM users WHERE {condition}",
                values
            )
            return [cls(*row) for row in rows]

    @classmethod
    def get(cls, **filters) -> list["User"]:

        keys = filters.keys()
        conditions = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters.values())

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT name, phone, role, id FROM users WHERE {conditions}",
                values
            )

            name, phone, role, id = rows[0]
            return [cls(id=id, name=name, phone=phone, role=role) for row in rows]
        
    def create(self) -> "User":
        with DatabaseConnection() as db:
            db.cur.execute(
                "INSERT INTO users (name, phone, role) VALUES (%s, %s, %s) RETURNING id",
                (self.name, self.phone, self.role)
            )

            self.id = db.cur.fetchone()[0]

            return self
        
    def update(self, **payload) -> "User | None":
        fields = ", ".join([f"{key} - %s" for key in payload])
        values = tuple(payload.values())

        if self.id is None:
            raise ValueError("Cannot update user without id")
        
        with DatabaseConnection() as db:
            db.cur.execute(
                f"UPDATE users SET {fields} WHERE id = %s RETURNING id, name, phone, role",
                (*values, self.id)
            )

            row = db.cur.fetchone()

        if not row:
            return None
        else:
            _, name, phone, role = row
            self.name = name
            self.phone = phone
            self.role = role

            return self
        
    def delete(self, id : int) -> bool :
        with DatabaseConnection() as db:
            db.cur.execute("DELETE FROM users WHERE id = %s", (id,))
            return db.cur.fetchone() is not None

@dataclass
class Dish:
    name: str 
    price: float
    description: str
    id: int | None = None

    @classmethod
    def all(cls) -> list["Dish"]:
        with DatabaseConnection() as db:
            rows = db.query("SELECT name, price, description, id FROM users")
            return [cls(*row) for row in rows]
        
    @classmethod
    def filter(cls, **filters) -> list["Dish"]:
        keys = filters.keys()

        condition = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters[key] for key in keys)

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT name, price, description, id FROM users WHERE {condition}",
                values
            )
            return [cls(*row) for row in rows]

    @classmethod
    def get(cls, **filters) -> list["Dish"]:

        keys = filters.keys()
        conditions = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters.values())

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT name, price, description, id FROM users WHERE {conditions}",
                values
            )

            name, price, description, id = rows[0]
            return [cls(id=id, name=name, price=price, description=description) for row in rows]
        
    def create(self) -> "Dish":
        with DatabaseConnection() as db:
            db.cur.execute(
                "INSERT INTO users (name, price, description) VALUES (%s, %s, %s) RETURNING id",
                (self.name, self.price, self.description)
            )

            self.id = db.cur.fetchone()[0]

            return self
        
    def update(self, **payload) -> "Dish | None":
        fields = ", ".join([f"{key} - %s" for key in payload])
        values = tuple(payload.values())

        if self.id is None:
            raise ValueError("Cannot update user without id")
        
        with DatabaseConnection() as db:
            db.cur.execute(
                f"UPDATE users SET {fields} WHERE id = %s RETURNING id, name, phone, description",
                (*values, self.id)
            )

            row = db.cur.fetchone()

        if not row:
            return None
        else:
            _, name, price, description = row
            self.name = name
            self.price = price
            self.description = description

            return self
        
    def delete(self, id : int) -> bool :
        with DatabaseConnection() as db:
            db.cur.execute("DELETE FROM users WHERE id = %s", (id,))
            return db.cur.fetchone() is not None

# ----------------------------------- ORDER ----------------------------- #

@dataclass
class Order:
    user_id: int
    datetime: str
    id: int | None = None

    @classmethod
    def all(cls) -> list["Order"]:
        with DatabaseConnection() as db:
            rows = db.query("SELECT user_id, datetime, id FROM users")
            return [cls(*row) for row in rows]
        
    @classmethod
    def filter(cls, **filters) -> list["Order"]:
        keys = filters.keys()

        condition = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters[key] for key in keys)

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT user_id, datetime, id FROM users WHERE {condition}",
                values
            )
            return [cls(*row) for row in rows]

    @classmethod
    def get(cls, **filters) -> list["Order"]:

        keys = filters.keys()
        conditions = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters.values())

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT user_id, datetime, id FROM users WHERE {conditions}",
                values
            )

            user_id, datetime, id = rows[0]
            return [cls(id=id, user_id=user_id, datetime=datetime) for row in rows]
        
    def create(self) -> "Order":
        with DatabaseConnection() as db:
            db.cur.execute(
                "INSERT INTO users (user_id, datetime) VALUES (%s, %s) RETURNING id",
                (self.user_id, self.datetime)
            )

            self.id = db.cur.fetchone()[0]

            return self
        
    def update(self, **payload) -> "Order | None":
        fields = ", ".join([f"{key} - %s" for key in payload])
        values = tuple(payload.values())

        if self.id is None:
            raise ValueError("Cannot update user without id")
        
        with DatabaseConnection() as db:
            db.cur.execute(
                f"UPDATE users SET {fields} WHERE id = %s RETURNING id, user_id, datetime",
                (*values, self.id)
            )

            row = db.cur.fetchone()

        if not row:
            return None
        else:
            _, user_id, datetime = row
            self.user_id = user_id
            self.datetime = datetime

            return self
        
    def delete(self, id : int) -> bool :
        with DatabaseConnection() as db:
            db.cur.execute("DELETE FROM users WHERE id = %s", (id,))
            return db.cur.fetchone() is not None
        
# ------------------------------ ORDER ITEM --------------------------------

@dataclass
class OrderItem:
    order_id: int
    dish_id: int
    amount: int
    id: int | None = None

    @classmethod
    def all(cls) -> list["OrderItem"]:
        with DatabaseConnection() as db:
            rows = db.query("SELECT order_id, dish_id, amount, id FROM users")
            return [cls(*row) for row in rows]
        
    @classmethod
    def filter(cls, **filters) -> list["OrderItem"]:
        keys = filters.keys()

        condition = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters[key] for key in keys)

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT order_id, dish_id, amount, id FROM users WHERE {condition}",
                values
            )
            return [cls(*row) for row in rows]

    @classmethod
    def get(cls, **filters) -> list["OrderItem"]:

        keys = filters.keys()
        conditions = " AND ".join([f"{key} = %s" for key in keys])
        values = tuple(filters.values())

        with DatabaseConnection() as db:
            rows = db.query(
                f"SELECT order_id, dish_id, amount, id FROM users WHERE {conditions}",
                values
            )

            order_id, dish_id, amount, id = rows[0]
            return [cls(id=id, order_id=order_id, dish_id = dish_id, amount=amount) for row in rows]
        
    def create(self) -> "OrderItem":
        with DatabaseConnection() as db:
            db.cur.execute(
                "INSERT INTO users (order_id, dish_id, amount) VALUES (%s, %s, %s) RETURNING id",
                (self.order_id, self.dish_id, self.amount)
            )

            self.id = db.cur.fetchone()[0]

            return self
        
    def update(self, **payload) -> "OrderItem | None":
        fields = ", ".join([f"{key} - %s" for key in payload])
        values = tuple(payload.values())

        if self.id is None:
            raise ValueError("Cannot update user without id")
        
        with DatabaseConnection() as db:
            db.cur.execute(
                f"UPDATE users SET {fields} WHERE id = %s RETURNING id, order_id, dish_id, amount",
                (*values, self.id)
            )

            row = db.cur.fetchone()

        if not row:
            return None
        else:
            _, order_id, dish_id, amount = row
            self.order_id = order_id
            self.dish_id = dish_id
            self.amount = amount

            return self
        
    def delete(self, id : int) -> bool :
        with DatabaseConnection() as db:
            db.cur.execute("DELETE FROM users WHERE id = %s", (id,))
            return db.cur.fetchone() is not None

