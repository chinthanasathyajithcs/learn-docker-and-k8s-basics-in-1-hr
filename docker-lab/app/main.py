import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psycopg2
import pika

APP_NAME = os.getenv("APP_NAME", "ifs-workorder-api")
APP_ENV  = os.getenv("APP_ENV", "dev")
DB_HOST  = os.getenv("DB_HOST", "db")
DB_USER  = os.getenv("DB_USER", "ifs")
DB_PASS  = os.getenv("DB_PASS", "ifs")
DB_NAME  = os.getenv("DB_NAME", "ifsdb")
RMQ_HOST = os.getenv("RMQ_HOST", "mq")

app = FastAPI(title="IFS Work Order API", version="0.1.0")

# Serve static files (logo) and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

EXCHANGE = "ifs.events"
QUEUE = "workorders"

class WorkOrder(BaseModel):
    id: int
    title: str
    status: str = "NEW"

def db_connect():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

def ensure_work_orders_table(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS work_orders (id INT PRIMARY KEY, title TEXT, status TEXT)")

def ensure_messaging():
    """Declare the fanout exchange, the workorders queue, and the binding."""
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

@app.get("/workorders")
def list_workorders():
    conn = db_connect()
    cur = conn.cursor()
    ensure_work_orders_table(cur)
    conn.commit()
    cur.execute("SELECT id, title, status FROM work_orders ORDER BY id")
    rows = [{"id": row[0], "title": row[1], "status": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

@app.post("/workorders")
def create_workorder(wo: WorkOrder):
    # Store minimal data in Postgres
    conn = db_connect()
    cur = conn.cursor()
    ensure_work_orders_table(cur)
    cur.execute(
        "INSERT INTO work_orders (id, title, status) VALUES (%s, %s, %s) "
        "ON CONFLICT (id) DO UPDATE SET title=EXCLUDED.title, status=EXCLUDED.status",
        (wo.id, wo.title, wo.status),
    )
    conn.commit()
    cur.close()
    conn.close()

    # Publish event to RabbitMQ. The queue is declared first, so the message is kept.
    mq_conn, ch = ensure_messaging()
    ch.basic_publish(exchange=EXCHANGE, routing_key="", body=f"wo.created:{wo.id}")
    mq_conn.close()

    return {"ok": True, "id": wo.id}
