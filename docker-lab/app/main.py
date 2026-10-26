import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psycopg2
import pika

APP_NAME = os.getenv("APP_NAME", "cashier")
APP_ENV  = os.getenv("APP_ENV", "dev")
DB_HOST  = os.getenv("DB_HOST", "cabinet")
DB_USER  = os.getenv("DB_USER", "sam")
DB_PASS  = os.getenv("DB_PASS", "sam")
DB_NAME  = os.getenv("DB_NAME", "stall")
RMQ_HOST = os.getenv("RMQ_HOST", "bell")

app = FastAPI(title="Sam's Burger Stall", version="0.1.0")

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

EXCHANGE = "stall.events"
QUEUE = "orders"

class Order(BaseModel):
    id: int
    item: str
    status: str = "NEW"

def db_connect():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

def ensure_orders_table(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS orders (id INT PRIMARY KEY, item TEXT, status TEXT)")

def ensure_messaging():
    """Declare the fanout exchange, the orders queue, and the binding."""
    mq_conn = pika.BlockingConnection(pika.ConnectionParameters(host=RMQ_HOST))
    ch = mq_conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="fanout", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE)
    return mq_conn, ch

@app.on_event("startup")
def setup_messaging():
    mq_conn, _ch = ensure_messaging()
    mq_conn.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": APP_NAME, "env": APP_ENV})

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": APP_NAME, "env": APP_ENV}

@app.get("/orders")
def list_orders():
    conn = db_connect()
    cur = conn.cursor()
    ensure_orders_table(cur)
    conn.commit()
    cur.execute("SELECT id, item, status FROM orders ORDER BY id")
    rows = [{"id": row[0], "item": row[1], "status": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

@app.post("/orders")
def create_order(order: Order):
    # File the order in the cabinet (Postgres)
    conn = db_connect()
    cur = conn.cursor()
    ensure_orders_table(cur)
    cur.execute(
        "INSERT INTO orders (id, item, status) VALUES (%s, %s, %s) "
        "ON CONFLICT (id) DO UPDATE SET item=EXCLUDED.item, status=EXCLUDED.status",
        (order.id, order.item, order.status),
    )
    conn.commit()
    cur.close()
    conn.close()

    # Ring the bell (RabbitMQ). The queue is declared first, so the message is kept.
    mq_conn, ch = ensure_messaging()
    ch.basic_publish(exchange=EXCHANGE, routing_key="", body=f"order.created:{order.id}")
    mq_conn.close()

    return {"ok": True, "id": order.id}
