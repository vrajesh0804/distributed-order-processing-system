# Distributed Event-Driven Order Processing System

A Python backend project built with **FastAPI + PostgreSQL + SQLAlchemy + Redis + Kafka**.

This project is designed as a portfolio-level backend system, not just CRUD. It demonstrates how real backend systems create an order quickly, publish an event, and let a background worker process inventory and payment asynchronously.

---

## What this backend does

1. Create users.
2. Create products.
3. Create an order with one or more products.
4. Store order in PostgreSQL with `PENDING` status.
5. Publish `order_created` event to Kafka.
6. Worker consumes Kafka event.
7. Worker checks inventory.
8. Worker simulates payment.
9. Worker updates order status to:
   - `PROCESSING`
   - `CONFIRMED`
   - `FAILED`
   - `OUT_OF_STOCK`
10. Redis caches order status for faster status reads.
11. Redis also handles simple rate limiting.

---

## Folder structure

```txt
distributed_order_backend/
│
├── app/
│   ├── main.py
│   │   └── FastAPI app entry point. Adds middleware and includes routers.
│   │
│   ├── api/
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── user.py
│   │   └── event.py
│   │   └── API route files. Each file manages one domain.
│   │
│   ├── core/
│   │   └── config.py
│   │   └── Reads environment variables from `.env`.
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── seed.py
│   │   └── Database engine, session, and sample data script.
│   │
│   ├── models/
│   │   └── database_model.py
│   │   └── SQLAlchemy database table models.
│   │
│   ├── schemas/
│   │   ├── product_schema.py
│   │   ├── order_schema.py
│   │   ├── user_schema.py
│   │   └── event_schema.py
│   │   └── Pydantic request and response models.
│   │
│   ├── services/
│   │   ├── order_service.py
│   │   ├── kafka_service.py
│   │   └── cache_service.py
│   │   └── Business logic, Kafka producer, Redis cache logic.
│   │
│   └── workers/
│       └── order_worker.py
│       └── Kafka consumer that processes orders asynchronously.
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Packages used and why

### FastAPI
Used to build REST APIs quickly with automatic Swagger documentation.

### Uvicorn
ASGI server used to run FastAPI.

### SQLAlchemy
ORM used to connect Python classes with PostgreSQL tables.

### psycopg2-binary
PostgreSQL database driver used by SQLAlchemy.

### Pydantic
Used for request validation and response serialization.

### pydantic-settings
Used to read environment variables cleanly.

### Redis
Used for order status caching and rate limiting.

### Kafka Python
Used to publish and consume Kafka events.

### Docker Compose
Used to run FastAPI, PostgreSQL, Redis, Kafka, Zookeeper, and worker together.

---

## Database tables

### users
Stores basic user data.

```txt
id
name
email
password
created_at
```

### products
Stores product catalog.

```txt
id
name
price
stock_quantity
```

### orders
Stores order status and totals.

```txt
id
user_id
status
total_amount
payment_status
inventory_status
created_at
updated_at
```

### order_items
Stores products inside each order.

```txt
id
order_id
product_id
quantity
price
```

### order_events
Stores event history for debugging and tracking.

```txt
id
order_id
event_type
payload
created_at
```

---

## How to run locally without Docker

### 1. Create virtual environment

```bash
python -m venv myenv
```

### 2. Activate virtual environment

Windows:

```bash
myenv\Scripts\activate
```

Linux/Mac:

```bash
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` to `.env` and update values if needed.

```bash
cp .env.example .env
```

### 5. Create PostgreSQL database

Create database:

```txt
distributed_order_system
```

### 6. Run API

```bash
uvicorn app.main:app --reload
```

Swagger will be available at:

```txt
http://127.0.0.1:8000/docs
```

### 7. Seed sample data

Open another terminal and run:

```bash
python -m app.db.seed
```

### 8. Run worker

```bash
python -m app.workers.order_worker
```

---

## How to run with Docker Compose

```bash
docker compose up --build
```

This starts:

- FastAPI API service
- PostgreSQL
- Redis
- Kafka
- Zookeeper
- Worker service

API URL:

```txt
http://127.0.0.1:8000/docs
```

---

## API usage flow

### 1. Create user

`POST /users/`

```json
{
  "name": "name",
  "email": "email@example.com",
  "password": "password"
}
```

### 2. Create product

`POST /products/`

```json
{
  "name": "Laptop",
  "price": 1510,
  "stock_quantity": 10
}
```

### 3. Create order

`POST /orders/`

```json
{
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

Expected response:

```json
{
  "id": 1,
  "user_id": 1,
  "status": "PENDING",
  "total_amount": 3020,
  "payment_status": "WAITING",
  "inventory_status": "WAITING",
  "items": []
}
```

The worker will later update the status.

### 4. Check order status

`GET /orders/1/status`

Possible response:

```json
{
  "order_id": 1,
  "status": "CONFIRMED",
  "payment_status": "SUCCESS",
  "inventory_status": "RESERVED",
  "message": "Order confirmed successfully"
}
```

### 5. Check order events

`GET /events/orders/1`

---
