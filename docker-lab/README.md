# Docker Lab: Run Sam's Burger Stall with Docker Compose

This is the first lab. Start here if Docker is new to you.

## The story

Sam runs a burger stall at a campus fair. At first Sam does everything alone, and everything the stall needs
to know is in Sam's head. That works until the stall has to run somewhere else, or with more people.

So Sam writes things down. The burger recipe goes on a card, and the stall becomes a small kitchen team. A plan
on the wall shows who does what:

| Helper | Job in the story | Technology |
|---|---|---|
| **Cashier** | Shows the web page and takes new orders | FastAPI (the `cashier` service) |
| **Filing cabinet** | Keeps every order | PostgreSQL (the `cabinet` service) |
| **Bell** | Rings once for every new order, so the team hears about it | RabbitMQ (the `bell` service) |
| **Notebook** | Listens for the bell and writes every order down | A small Python program (the `notebook` service) |

**Docker Compose** reads the plan on the wall (`docker-compose.yml`), starts all four helpers, connects them on
a private network, and starts them in the right order.

## Words you need first

| Word | Meaning in plain English |
|---|---|
| **Image** | A recipe card. It is built once and never changes. |
| **Container** | A box packed from the recipe card: a running copy of the image. You can stop it, throw it away and pack a new one. |
| **Compose** | The plan on the wall. One file that starts several containers together. |
| **Port** | A numbered door. `9000:9000` means "door 9000 on your computer leads to door 9000 inside the container." |
| **Network** | A private corridor. Containers find each other by name, for example the cashier reaches the cabinet at `cabinet`. |
| **Volume** | A locker. What is inside stays when the container is thrown away. |

## Before you start

1. **Install Docker with Compose.**
   - Windows or Mac: install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
   - Linux or WSL: install [Docker Engine](https://docs.docker.com/engine/install/) and the Compose plugin.
2. **Use Wi-Fi for the first start.** The first start downloads about 0.3 GB of images, plus the system and
   Python packages the build needs. Do not do this on mobile data. Once the images are on your computer, later starts
   need no download. A classmate can also give you the images as a file: see
   [Offline setup](../README.md#offline-setup).
3. **Have a terminal and a web browser ready.**

## Lab steps

### Step 1: Check that Docker is running

```bash
docker --version
docker compose version
docker info
```

You should see version numbers and some information about your Docker installation.
If you see `Cannot connect to the Docker daemon`, start Docker Desktop and wait until it says it is running.

### Step 2: Go to the project folder

From the root of this repository:

```bash
cd docker-lab
```

Look at the plan. The four helpers are listed under `services:`:

```bash
grep -E '^  [a-z]+:' docker-compose.yml
```

You should see `cabinet`, `bell`, `cashier` and `notebook`.

### Step 3: Start everything

```bash
docker compose up --build -d
```

- `up` creates and starts the containers.
- `--build` builds the cashier and the notebook from their recipe card, the `Dockerfile`. They share one
  recipe and do different jobs: the notebook's `command:` in `docker-compose.yml` starts a different program.
- `-d` runs everything in the background, so your terminal is free again.

You will see lines such as `Container docker-lab-cabinet-1 Started`. The first start takes several minutes
because of the downloads.

### Step 4: Check that every helper is on duty

```bash
docker compose ps
```

Wait a minute, then check again. You want to see all four helpers with the status `healthy`.
`healthy` means the helper passed its own check.

To watch the start-up messages, run:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop watching. This does **not** stop the helpers.

### Step 5: Ask the cashier if the stall is open

Open <http://localhost:9000/healthz> in your browser. You should see:

```json
{"status":"ok","service":"cashier","env":"dev"}
```

This is the health check. It is the first thing to try when something seems wrong.

### Step 6: Place your first order

Open <http://localhost:9000>. Fill in the **Place an Order** form:

| Field | Value |
|---|---|
| Order number | `1001` |
| Item | `Cheeseburger` |
| Status | `NEW` |

Select **Place order**. You should see `Saved order 1001.` and the order should appear in the **Orders**
table.

Behind the scenes, the cashier did two things:

1. Filed the order in the **filing cabinet** (PostgreSQL).
2. Rang the **bell** (RabbitMQ) with the message `order.created:1001`.

**Try it:** submit order `1001` again with the status `COOKING`. The table still has one row for `1001`, but
its status changed. The same order is updated, not duplicated.

Prefer the command line? On macOS, Linux, Git Bash or WSL:

```bash
curl -X POST http://localhost:9000/orders \
  -H "Content-Type: application/json" \
  -d '{"id":1001,"item":"Cheeseburger","status":"NEW"}'
```

On Windows PowerShell:

```powershell
$body = @{ id = 1001; item = "Cheeseburger"; status = "NEW" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:9000/orders" -Method Post -ContentType "application/json" -Body $body
```

### Step 7: Look inside the filing cabinet

The raw data is at <http://localhost:9000/orders>. You should see your order as JSON.

You can also ask the database directly:

```bash
docker compose exec cabinet psql -U sam -d stall -c "SELECT * FROM orders;"
```

`docker compose exec cabinet` means "run a command inside the `cabinet` container." The output is a small
table with your order.

### Step 8: Hear the bell

1. Open <http://localhost:15672> and sign in with `guest` / `guest`.
2. Open **Queues and Streams**. You should see two queues: `orders` and `notebook`. The bell gives every
   queue its own copy of each message.
3. Select the **orders** queue, open **Get messages** and request one message.

The message body is `order.created:1001`. That is the bell the cashier rang in step 6. Nobody reads the
`orders` queue, so the messages wait there for you. The `notebook` queue is empty, because the notebook
reads its copies straight away.

### Step 9: Read the notebook

The notebook heard the bell and wrote the order down:

```bash
docker compose logs notebook
```

You should see a line such as `2026-10-26T09:15:02 order.created:1001`. The notebook keeps the same lines in a
file:

```bash
docker compose exec notebook cat /notebook/orders.log
```

Place another order in the browser and run the command again. A new line appears.

### Step 10: The lunch rush

At lunchtime, one cashier cannot keep up. Can you start more cashiers?

```bash
docker compose up -d --scale cashier=3
```

It fails with `Bind for 0.0.0.0:9000 failed: port is already allocated`. Only one container can own door 9000
on your computer, so the second and third cashiers cannot open. Go back to one cashier:

```bash
docker compose up -d --scale cashier=1
```

Now make the cashier collapse, as if the program crashed:

```bash
docker compose kill cashier
docker compose ps -a
```

The cashier shows `Exited`, and <http://localhost:9000> no longer opens. Nothing brings it back. Docker did
what you asked, once. It does not watch the stall for you. Reopen it yourself:

```bash
docker compose start cashier
```

**Question:** What would the stall need to survive a lunch rush, or a cashier who collapses? Several
cashiers on several computers, one front desk that sends customers to whichever cashier is free, and a
manager who replaces anyone who stops. That is what Kubernetes does, in the [Kubernetes lab](../k8s-lab/README.md).

### Step 11: Break it on purpose

The cashier depends on the filing cabinet. Test what happens when the cabinet is closed:

```bash
docker compose stop cabinet
```

Place a new order in the browser. The page should say `Could not save the order.` Find out why in the
cashier's logs:

```bash
docker compose logs cashier
```

Near the end you will see `500 Internal Server Error` and `could not translate host name "cabinet"`. The
cashier looked for the cabinet by name, and nobody answered. Reopen the cabinet:

```bash
docker compose start cabinet
```

Place the order again. It works.

### Step 12: Stop, start and reset

Stop the helpers, but keep the data:

```bash
docker compose down
```

Start them again without rebuilding:

```bash
docker compose up -d
```

Open <http://localhost:9000/orders>. Order `1001` is still there, and the notebook still has its lines.
`down` deleted the containers, but the cabinet keeps its papers in a **named volume** called `cabinet-papers`,
and the notebook keeps its pages in one called `notebook-pages` (see `volumes:` in `docker-compose.yml`). The
new containers picked them up again. See them with:

```bash
docker volume ls
```

Delete everything, including the stored data, for a clean start:

```bash
docker compose down -v
```

Use this only when you want to remove the orders and the notebook. The next `up` starts from empty.

## Rebuild after changing the code

Changed `app/main.py`, `app/notebook.py`, `Dockerfile` or a file under `app/`? Rebuild:

```bash
docker compose up --build -d
```

## Service addresses and ports

| Service | Address from your computer | What it is |
|---|---|---|
| Application | <http://localhost:9000> | The cashier: web page and order API |
| Health check | <http://localhost:9000/healthz> | Is the stall open? |
| RabbitMQ UI | <http://localhost:15672> | The bell's control room (`guest` / `guest`) |
| RabbitMQ messages | `localhost:5672` | The bell's messaging port (not a web page) |
| PostgreSQL | `localhost:5433` | The filing cabinet (user `sam`, password `sam`, database `stall`) |

PostgreSQL and RabbitMQ messages are not websites. Opening their ports in a browser shows nothing.

## Project structure

```text
docker-lab/
├── app/
│   ├── main.py                    # The cashier: web page and order API
│   ├── notebook.py                # The notebook: listens for the bell, writes orders down
│   ├── requirements.txt           # Python packages they need
│   ├── static/                    # Files the web page serves as they are
│   └── templates/index.html       # The web page
├── Dockerfile                     # The recipe card for the cashier and the notebook
├── docker-compose.yml             # The plan on the wall for all four helpers
├── Makefile                       # Optional shortcuts
└── README.md
```

## Troubleshooting

**`Cannot connect to the Docker daemon`**
Start Docker Desktop, or on Linux or WSL start the Docker service and wait for it to be ready.

**`permission denied` when running `docker`** (Linux or WSL)
Follow Docker's [post-install steps](https://docs.docker.com/engine/install/linux-postinstall/) to add your
user to the `docker` group. Sign out and back in, then run `docker info` again.
Do not make the Docker socket world-writable.

**`port is already allocated`**
Another program uses one of the ports, such as 9000 or 15672. Stop that program, or change the left-hand
number in `docker-compose.yml`. For example, `"9001:9000"` makes the app open at <http://localhost:9001>.
In step 10 this error is expected: it is the lesson.

**Build fails with `fs.read` privileges**
Some Docker Compose versions need a workaround.

macOS, Linux, Git Bash or WSL:

```bash
BUILDX_BAKE_ENTITLEMENTS_FS=0 docker compose up --build -d
```

Windows PowerShell:

```powershell
$env:BUILDX_BAKE_ENTITLEMENTS_FS = "0"
docker compose up --build -d
```

**Something is stuck**
Look at one helper's logs:

```bash
docker compose logs cashier
docker compose logs cabinet
docker compose logs bell
docker compose logs notebook
```

> This lab uses simple passwords so it is easy to learn with.
> Do not deploy this configuration to production or expose it to the internet.

## Next

When you are comfortable with Compose, move on to the [Kubernetes lab](../k8s-lab/README.md).
