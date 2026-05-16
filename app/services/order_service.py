"""
Order business logic.

Routes should stay thin. Real backend projects keep business rules in service
files like this one.
"""

import json
from sqlalchemy.orm import Session

from app.models import database_model
from app.schemas.order_schema import OrderCreate
from app.services.cache_service import cache_order_status
from app.services.kafka_service import publish_order_created_event


def create_order(db: Session, order_request: OrderCreate) -> database_model.Order:
    """
    Create order in PENDING state and publish Kafka event for async processing.

    Steps:
    1. Validate product IDs and calculate total amount.
    2. Save order and order items in PostgreSQL.
    3. Store order_created event in order_events table.
    4. Publish same event to Kafka.
    """
    total_amount = 0.0
    order_items_data = []

    for item in order_request.items:
        product = db.query(database_model.Product).filter(database_model.Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product {item.product_id} not found")

        line_total = product.price * item.quantity
        total_amount += line_total
        order_items_data.append({"product": product, "quantity": item.quantity, "price": product.price})

    order = database_model.Order(
        user_id=order_request.user_id,
        status="PENDING",
        total_amount=total_amount,
        payment_status="WAITING",
        inventory_status="WAITING",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item_data in order_items_data:
        db.add(
            database_model.OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price=item_data["price"],
            )
        )

    event_data = {
        "event_type": "order_created",
        "order_id": order.id,
        "user_id": order.user_id,
        "items": [item.model_dump() for item in order_request.items],
        "total_amount": order.total_amount,
    }

    db.add(database_model.OrderEvent(order_id=order.id, event_type="order_created", payload=json.dumps(event_data)))
    db.commit()
    db.refresh(order)

    cache_order_status(
        order.id,
        {
            "order_id": order.id,
            "status": order.status,
            "payment_status": order.payment_status,
            "inventory_status": order.inventory_status,
            "message": "Order received and waiting for worker processing",
        },
    )

    publish_order_created_event(event_data)
    return order
