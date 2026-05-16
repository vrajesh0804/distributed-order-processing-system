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

## Important backend concepts explained

### Why use SQLAlchemy models?

SQLAlchemy models represent database tables. Example: `Product` class becomes a `products` table.

### Why use Pydantic schemas?

Pydantic schemas control API request and response data. This prevents exposing sensitive fields like passwords.

### Why use `response_model`?

`response_model` tells FastAPI what the API response should look like. It validates and formats the response.

### Why use APIRouter?

APIRouter keeps route files separate. This avoids putting everything in `main.py` and prevents circular imports.

### Why use Kafka?

Kafka allows asynchronous event-driven processing. The API creates the order and publishes an event. The worker processes the order later.

### Why use Redis?

Redis is fast in-memory storage. It is used here for caching order status and rate limiting.

---

## What tasks from your 31-task list this backend covers

Completed/covered in this backend:

- Task 1: Setup FastAPI Project
- Task 2: Setup SQLAlchemy Models
- Task 3: Setup PostgreSQL Database
- Task 4: Build Product APIs
- Task 5: Build Order APIs
- Task 6: Add Pydantic Schemas
- Task 7: Setup Docker
- Task 8: Setup Docker Compose
- Task 9: Setup Kafka Producer
- Task 10: Create Worker Service
- Task 11: Implement Inventory Processing
- Task 12: Implement Fake Payment Processing
- Task 13: Implement Order Status Updates
- Task 14: Setup Redis
- Task 15: Add Redis Caching
- Task 16: Add Rate Limiting
- Task 22: Add Logging-style worker prints
- Task 23: Basic exception handling
- Task 24: Swagger API documentation
- Task 29: README

Not included yet:

- Alembic migrations
- Kubernetes manifests
- Cloud deployment
- Architecture diagram image
- Frontend integration folder

---

## Recommended next improvements

1. Add Alembic migrations.
2. Add proper password hashing with bcrypt.
3. Add JWT authentication.
4. Add structured logging.
5. Add Kubernetes YAML files.
6. Add unit tests.
7. Connect frontend to `/orders/` and `/orders/{id}/status`.

---

## Project title for LinkedIn

**Distributed Event-Driven Order Processing System using FastAPI, Kafka, Redis, and PostgreSQL**

Good LinkedIn line:

> Built a distributed event-driven backend system in Python using FastAPI, PostgreSQL, Kafka, Redis, and Docker Compose. The system creates orders synchronously, publishes events to Kafka, and processes inventory/payment asynchronously using a worker service.
