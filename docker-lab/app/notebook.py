import os
from datetime import datetime
import pika

# The notebook keeper: listens for the bell and writes down every order.

RMQ_HOST = os.getenv("RMQ_HOST", "bell")
NOTEBOOK = os.getenv("NOTEBOOK_FILE", "/notebook/orders.log")

EXCHANGE = "stall.events"
QUEUE = "notebook"

def write_down(ch, method, _properties, body):
    line = f"{datetime.now().isoformat(timespec='seconds')} {body.decode()}"
    with open(NOTEBOOK, "a") as notebook:
        notebook.write(line + "\n")
    print(line, flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Open the notebook, so it exists before the first order arrives
    open(NOTEBOOK, "a").close()

    mq_conn = pika.BlockingConnection(pika.ConnectionParameters(host=RMQ_HOST))
    ch = mq_conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="fanout", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE)
    ch.basic_consume(queue=QUEUE, on_message_callback=write_down)
    print(f"Notebook open at {NOTEBOOK}. Listening for the bell.", flush=True)
    ch.start_consuming()

if __name__ == "__main__":
    main()
