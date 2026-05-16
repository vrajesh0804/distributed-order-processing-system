"""
Kafka worker service.

Run this worker separately from the FastAPI API server.
It listens to order_created events and processes inventory/payment in background.
"""

import json
import random
import time
from kafka import KafkaConsumer

from app.core.config import settings
from app.db.database import SessionLocal
from app.models import database_model
from app.services.cache_service import cache_order_status


def update_order_status_cache(order: database_model.Order, message: str) -> None:
    """Store latest order status in Redis for fast status API responses."""
    cache_order_status(
        order.id,
        {
            "order_id": order.id,
            "status": order.status,
            "payment_status": order.payment_status,
            "inventory_status": order.inventory_status,
            "message": message,
        },
    )


def process_inventory(db, order: database_model.Order) -> bool:
    """
    Check and reserve product stock.

    Returns True if all products have enough stock, otherwise False.
    """
    for item in order.items:
        product = db.query(database_model.Product).filter(database_model.Product.id == item.product_id).first()
        if not product or product.stock_quantity < item.quantity:
            order.status = "OUT_OF_STOCK"
            order.inventory_status = "FAILED"
            order.payment_status = "CANCELLED"
            db.commit()
            update_order_status_cache(order, "Order failed because product is out of stock")
            return False

    for item in order.items:
        product = db.query(database_model.Product).filter(database_model.Product.id == item.product_id).first()
        product.stock_quantity -= item.quantity

    order.inventory_status = "RESERVED"
    db.commit()
    update_order_status_cache(order, "Inventory reserved successfully")
    return True


def process_fake_payment(db, order: database_model.Order) -> bool:
    """
    Simulate payment processing.

    Random success/failure helps demonstrate asynchronous status updates.
    """
    time.sleep(2)
    payment_success = random.choice([True, True, True, False])

    if payment_success:
        order.payment_status = "SUCCESS"
        db.commit()
        update_order_status_cache(order, "Payment completed successfully")
        return True

    order.status = "FAILED"
    order.payment_status = "FAILED"
    db.commit()
    update_order_status_cache(order, "Payment failed")
    return False


def process_order(event_data: dict) -> None:
    """Main worker function that processes one order_created event."""
    db = SessionLocal()
    try:
        order = db.query(database_model.Order).filter(database_model.Order.id == event_data["order_id"]).first()
        if not order:
            print(f"Order not found: {event_data['order_id']}")
            return

        print(f"Processing order: {order.id}")
        order.status = "PROCESSING"
        db.commit()
        update_order_status_cache(order, "Worker started processing order")

        inventory_ok = process_inventory(db, order)
        if not inventory_ok:
            return

        payment_ok = process_fake_payment(db, order)
        if not payment_ok:
            return

        order.status = "CONFIRMED"
        db.add(
            database_model.OrderEvent(
                order_id=order.id,
                event_type="order_confirmed",
                payload=json.dumps({"order_id": order.id, "status": "CONFIRMED"}),
            )
        )
        db.commit()
        update_order_status_cache(order, "Order confirmed successfully")
        print(f"Order confirmed: {order.id}")
    finally:
        db.close()


def start_worker() -> None:
    """Start Kafka consumer loop."""
    consumer = KafkaConsumer(
        settings.ORDER_CREATED_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda message: json.loads(message.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="order-worker-group",
    )

    print("Order worker started. Waiting for Kafka events...")
    for message in consumer:
        print(f"Received event: {message.value}")
        process_order(message.value)


if __name__ == "__main__":
    start_worker()
