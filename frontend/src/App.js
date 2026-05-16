import React, { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

const emptyProduct = { name: "", price: "", stock_quantity: "" };
const emptyUser = { name: "", email: "", password: "" };
const emptyOrder = { user_id: "", product_id: "", quantity: 1 };

function App() {
  const [products, setProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedOrderId, setSelectedOrderId] = useState("");
  const [orderStatus, setOrderStatus] = useState(null);

  const [productForm, setProductForm] = useState(emptyProduct);
  const [userForm, setUserForm] = useState(emptyUser);
  const [orderForm, setOrderForm] = useState(emptyOrder);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Ready. Start by creating a user and product.");
  const [error, setError] = useState("");

  const totalInventoryValue = useMemo(() => {
    return products.reduce((sum, product) => sum + product.price * product.stock_quantity, 0);
  }, [products]);

  async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });

    const contentType = response.headers.get("content-type");
    const data = contentType && contentType.includes("application/json") ? await response.json() : null;

    if (!response.ok) {
      throw new Error(data?.detail || "API request failed");
    }

    return data;
  }

  async function loadDashboardData() {
    setError("");
    try {
      const [productData, userData] = await Promise.all([
        apiRequest("/products/"),
        apiRequest("/users/"),
      ]);
      setProducts(productData);
      setUsers(userData);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function createProduct(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        name: productForm.name,
        price: Number(productForm.price),
        stock_quantity: Number(productForm.stock_quantity),
      };

      const createdProduct = await apiRequest("/products/", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setProducts((current) => [createdProduct, ...current]);
      setProductForm(emptyProduct);
      setMessage(`Product created: ${createdProduct.name}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function createUser(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const createdUser = await apiRequest("/users/", {
        method: "POST",
        body: JSON.stringify(userForm),
      });

      setUsers((current) => [createdUser, ...current]);
      setUserForm(emptyUser);
      setMessage(`User created: ${createdUser.name}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function createOrder(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        user_id: Number(orderForm.user_id),
        items: [
          {
            product_id: Number(orderForm.product_id),
            quantity: Number(orderForm.quantity),
          },
        ],
      };

      const createdOrder = await apiRequest("/orders/", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setOrders((current) => [createdOrder, ...current]);
      setSelectedOrderId(createdOrder.id);
      setOrderStatus({
        order_id: createdOrder.id,
        status: createdOrder.status,
        payment_status: createdOrder.payment_status,
        inventory_status: createdOrder.inventory_status,
        message: "Order created. Kafka worker should process it in background.",
      });
      setMessage(`Order #${createdOrder.id} created and Kafka event published`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function checkOrderStatus(orderId = selectedOrderId) {
    if (!orderId) return;
    setError("");

    try {
      const status = await apiRequest(`/orders/${orderId}/status`);
      setOrderStatus(status);
      setMessage(`Order #${orderId} status loaded from Redis/PostgreSQL`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadOrderEvents(orderId = selectedOrderId) {
    if (!orderId) return;
    setError("");

    try {
      const eventData = await apiRequest(`/events/orders/${orderId}`);
      setEvents(eventData);
      setMessage(`Loaded ${eventData.length} events for order #${orderId}`);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!selectedOrderId) return;

    const timer = setInterval(() => {
      checkOrderStatus(selectedOrderId);
    }, 4000);

    return () => clearInterval(timer);
  }, [selectedOrderId]);

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">FastAPI Distributed Backend Dashboard</p>
          <h1>Event-Driven Order Processing System</h1>
          <p className="hero-text">
            React frontend connected to FastAPI, PostgreSQL, Redis cache, Kafka events, and worker processing.
          </p>
        </div>
        <div className="hero-card">
          <span>API Server</span>
          <strong>{API_BASE_URL}</strong>
          <button className="ghost-button" onClick={loadDashboardData}>Refresh Data</button>
        </div>
      </header>

      {error && <div className="alert error">{error}</div>}
      {message && <div className="alert success">{message}</div>}

      <section className="stats-grid">
        <div className="stat-card">
          <span>Products</span>
          <strong>{products.length}</strong>
        </div>
        <div className="stat-card">
          <span>Users</span>
          <strong>{users.length}</strong>
        </div>
        <div className="stat-card">
          <span>Frontend Orders</span>
          <strong>{orders.length}</strong>
        </div>
        <div className="stat-card">
          <span>Inventory Value</span>
          <strong>₹{totalInventoryValue.toLocaleString("en-IN")}</strong>
        </div>
      </section>

      <main className="main-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>Create Product</h2>
            <span>PostgreSQL</span>
          </div>
          <form onSubmit={createProduct} className="form-stack">
            <input placeholder="Product name" value={productForm.name} onChange={(e) => setProductForm({ ...productForm, name: e.target.value })} required />
            <input placeholder="Price" type="number" value={productForm.price} onChange={(e) => setProductForm({ ...productForm, price: e.target.value })} required />
            <input placeholder="Stock quantity" type="number" value={productForm.stock_quantity} onChange={(e) => setProductForm({ ...productForm, stock_quantity: e.target.value })} required />
            <button disabled={loading}>{loading ? "Saving..." : "Create Product"}</button>
          </form>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Create User</h2>
            <span>PostgreSQL</span>
          </div>
          <form onSubmit={createUser} className="form-stack">
            <input placeholder="Name" value={userForm.name} onChange={(e) => setUserForm({ ...userForm, name: e.target.value })} required />
            <input placeholder="Email" type="email" value={userForm.email} onChange={(e) => setUserForm({ ...userForm, email: e.target.value })} required />
            <input placeholder="Password" type="password" value={userForm.password} onChange={(e) => setUserForm({ ...userForm, password: e.target.value })} required />
            <button disabled={loading}>{loading ? "Saving..." : "Create User"}</button>
          </form>
        </section>

        <section className="panel order-panel">
          <div className="panel-header">
            <h2>Create Order</h2>
            <span>PostgreSQL + Kafka + Redis</span>
          </div>
          <form onSubmit={createOrder} className="form-stack">
            <select value={orderForm.user_id} onChange={(e) => setOrderForm({ ...orderForm, user_id: e.target.value })} required>
              <option value="">Select user</option>
              {users.map((user) => <option key={user.id} value={user.id}>{user.name} — {user.email}</option>)}
            </select>

            <select value={orderForm.product_id} onChange={(e) => setOrderForm({ ...orderForm, product_id: e.target.value })} required>
              <option value="">Select product</option>
              {products.map((product) => <option key={product.id} value={product.id}>{product.name} — ₹{product.price} — Stock {product.stock_quantity}</option>)}
            </select>

            <input placeholder="Quantity" type="number" min="1" value={orderForm.quantity} onChange={(e) => setOrderForm({ ...orderForm, quantity: e.target.value })} required />
            <button disabled={loading}>{loading ? "Creating..." : "Create Order"}</button>
          </form>
        </section>

        <section className="panel status-panel">
          <div className="panel-header">
            <h2>Order Status</h2>
            <span>Redis first, DB fallback</span>
          </div>
          <div className="status-actions">
            <input placeholder="Order ID" value={selectedOrderId} onChange={(e) => setSelectedOrderId(e.target.value)} />
            <button onClick={() => checkOrderStatus()}>Check Status</button>
            <button className="secondary" onClick={() => loadOrderEvents()}>Load Events</button>
          </div>

          {orderStatus ? (
            <div className="status-card">
              <div>
                <span>Order #{orderStatus.order_id}</span>
                <strong className={`badge ${String(orderStatus.status).toLowerCase()}`}>{orderStatus.status}</strong>
              </div>
              <p><b>Payment:</b> {orderStatus.payment_status}</p>
              <p><b>Inventory:</b> {orderStatus.inventory_status}</p>
              <p><b>Message:</b> {orderStatus.message}</p>
            </div>
          ) : (
            <div className="empty-state">Create or select an order to see status.</div>
          )}
        </section>
      </main>

      <section className="data-grid">
        <div className="table-card">
          <h2>Products</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Name</th><th>Price</th><th>Stock</th></tr></thead>
              <tbody>
                {products.map((p) => <tr key={p.id}><td>{p.id}</td><td>{p.name}</td><td>₹{p.price}</td><td>{p.stock_quantity}</td></tr>)}
              </tbody>
            </table>
          </div>
        </div>

        <div className="table-card">
          <h2>Users</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
              <tbody>
                {users.map((u) => <tr key={u.id}><td>{u.id}</td><td>{u.name}</td><td>{u.email}</td></tr>)}
              </tbody>
            </table>
          </div>
        </div>

        <div className="table-card wide">
          <h2>Order Events</h2>
          {events.length === 0 ? <div className="empty-state">No events loaded yet.</div> : (
            <div className="event-list">
              {events.map((event) => (
                <div className="event-item" key={event.id}>
                  <strong>{event.event_type}</strong>
                  <span>Order #{event.order_id}</span>
                  <pre>{event.payload}</pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default App;
