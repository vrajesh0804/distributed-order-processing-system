"""Seed script for creating sample users and products."""

from app.db.database import Base, SessionLocal, engine
from app.models.database_model import Product, User


def seed_data():
    """Create tables and insert starter data if database is empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(name="Test", email="test@example.com", password="password"))

        if db.query(Product).count() == 0:
            db.add_all(
                [
                    Product(name="iPhone 15", price=79999, stock_quantity=12),
                    Product(name="MacBook Air", price=114999, stock_quantity=6),
                    Product(name="Sony Headphones", price=19999, stock_quantity=25),
                ]
            )

        db.commit()
        print("Seed data inserted successfully")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
