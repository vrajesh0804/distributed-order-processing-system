# React Frontend for Distributed Order Backend

## What this frontend connects to

The backend API URL is inside `src/App.js`:

```js
const API_BASE_URL = "http://127.0.0.1:8000";
```

## Used APIs

- `GET /products/` — load products
- `POST /products/` — create product
- `GET /users/` — load users
- `POST /users/` — create user
- `POST /orders/` — create order; backend stores order in PostgreSQL and publishes Kafka event
- `GET /orders/{order_id}/status` — checks Redis first, then PostgreSQL fallback
- `GET /events/orders/{order_id}` — shows stored order events

## How data flows

```txt
React Form
  ↓
FastAPI endpoint
  ↓
PostgreSQL stores users/products/orders
  ↓
Kafka receives order_created event
  ↓
Worker processes order
  ↓
Redis stores latest order status cache
```

## Run frontend

```bash
cd frontend
npm install
npm start
```

Then open:

```txt
http://localhost:3000
```

Make sure backend runs at:

```txt
http://127.0.0.1:8000
```
