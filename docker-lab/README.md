# Docker Lab: Run a Work Order App with Docker Compose

This is the first lab. Start here if Docker is new to you.

## The story

A small factory has machines that break down. When a machine needs fixing, someone writes a
**work order**: "Replace pump seal on Line 3." The factory wants a web app that:

1. Saves every work order.
2. Announces each new work order to the maintenance team.
3. Keeps a log of what happens, so the IT team can search it later.

The app is not one big program. It is six small helpers working together:

| Helper | Job in the story | Technology |
|---|---|---|
| **Front desk** | Shows the web page and takes new work orders | FastAPI (the `api` service) |
| **Filing cabinet** | Stores every work order | PostgreSQL (the `db` service) |
| **Announcement board** | Tells the team "a new work order exists" | RabbitMQ (the `mq` service) |
| **Log collector** | Collects notes from the front desk | Logstash (the `logstash` service) |
| **Log library** | Stores and indexes all the notes | Elasticsearch (the `elasticsearch` service) |
| **Log search screen** | Lets you search the notes in a browser | Kibana (the `kibana` service) |

**Docker Compose** is the site manager. It reads one plan file (`docker-compose.yml`), starts all six
helpers, connects them on a private network, and starts them in the right order.

## Words you need first

| Word | Meaning in plain English |
|---|---|
| **Image** | A recipe. It is downloaded once and never changes. |
| **Container** | A running copy of an image, like a meal cooked from a recipe. You can stop it, delete it and cook it again. |
| **Compose** | A tool that starts several containers from one plan file. |
| **Port** | A numbered door. `9000:9000` means "door 9000 on your computer leads to door 9000 inside the container." |
| **Network** | A private corridor. Containers find each other by name, for example the API connects to the database at `db`. |
| **Volume** | A storage box that survives when a container is deleted. |

## Before you start

1. **Install Docker with Compose.**
   - Windows or Mac: install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
   - Linux or WSL: install [Docker Engine](https://docs.docker.com/engine/install/) and the Compose plugin.
2. **Use Wi-Fi for the first start.** The first start downloads about 1.8 GB of images, plus a few Python
   packages for the build. Do not do this on mobile data. Once the images are on your computer, later starts
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

Look at the plan. The six helpers are listed under `services:`:

```bash
grep -E '^  [a-z]+:' docker-compose.yml
```

You should see `elasticsearch`, `logstash`, `kibana`, `db`, `mq` and `api`.

### Step 3: Start everything

```bash
docker compose up --build -d
```

- `up` creates and starts the containers.
- `--build` builds the front desk (the `api`) from its recipe in `Dockerfile`.
- `-d` runs everything in the background, so your terminal is free again.

You will see lines such as `Container docker-lab-db-1 Started`. The first start takes several minutes
because of the downloads.

### Step 4: Check that every helper is on duty

```bash
docker compose ps
```

Wait 1 to 3 minutes, then check again. You want to see:

- `api`, `db`, `mq`, `elasticsearch` and `logstash` with the status `healthy`.
  `healthy` means the helper passed its own check.
- `kibana` as `running`. Kibana can take another minute before its web page opens.

To watch the start-up messages, run:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop watching. This does **not** stop the helpers.

### Step 5: Ask the front desk if it is open

Open <http://localhost:9000/healthz> in your browser. You should see:

```json
{"status":"ok","service":"ifs-workorder-api","env":"dev"}
```

This is the health check. It is the first thing to try when something seems wrong.

### Step 6: Log your first work order

Open <http://localhost:9000>. Fill in the **Submit a Work Order** form:

| Field | Value |
|---|---|
| ID | `1001` |
| Title | `Replace pump seal` |
| Status | `NEW` |

Select **Submit**. You should see `Saved work order 1001.` and the order should appear in the
**Work Orders** table.

Behind the scenes, the front desk did two things:

1. Wrote the order to the **filing cabinet** (PostgreSQL).
2. Posted a message `wo.created:1001` to the **announcement board** (RabbitMQ).

**Try it:** submit ID `1001` again with the status `IN_PROGRESS`. The table still has one row for
`1001`, but its status changed. The same order is updated, not duplicated.

Prefer the command line? On macOS, Linux, Git Bash or WSL:

```bash
curl -X POST http://localhost:9000/workorders \
  -H "Content-Type: application/json" \
  -d '{"id":1001,"title":"Replace pump seal","status":"NEW"}'
```

On Windows PowerShell:

```powershell
$body = @{ id = 1001; title = "Replace pump seal"; status = "NEW" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:9000/workorders" -Method Post -ContentType "application/json" -Body $body
```

### Step 7: Look inside the filing cabinet

The raw data is at <http://localhost:9000/workorders>. You should see your order as JSON.

You can also ask the database directly:

```bash
docker compose exec db psql -U ifs -d ifsdb -c "SELECT * FROM work_orders;"
```

`docker compose exec db` means "run a command inside the `db` container." The output is a small table with
your work order.

### Step 8: Read the announcement

1. Open <http://localhost:15672> and sign in with `guest` / `guest`.
2. Open **Queues and Streams**, then select the **workorders** queue. The API created it for you.
3. Open **Get messages** and request one message.

The message body is `wo.created:1001`. That is the announcement the front desk sent in step 6.

### Step 9: Search the logs

Every time the front desk handles a request, it writes a note. Those notes travel to the log library, and
Kibana lets you search them.

1. Open <http://localhost:5601>.
2. Open **Discover**. If you are asked to create a data view, create one with:
   - Name or index pattern: `nsbm-logs-*`
   - Timestamp field: `@timestamp`
3. Search for `1001` or `workorders`.

If nothing appears yet, wait 30 seconds, then refresh. Logs can take a moment to arrive.

### Step 10: Stop, start and reset

Stop the helpers, but keep the data:

```bash
docker compose down
```

Start them again without rebuilding:

```bash
docker compose up -d
```

Open <http://localhost:9000/workorders>. Order `1001` is still there. `down` deleted the containers, but the
filing cabinet keeps its papers in a **named volume** called `pgdata` (see `volumes:` in
`docker-compose.yml`), and the new `db` container picked it up again. See it with:

```bash
docker volume ls
```

Delete everything, including the stored data, for a clean start:

```bash
docker compose down -v
```

Use this only when you want to remove the work orders and logs. The next `up` starts from empty.

### Challenge: break it on purpose

The front desk depends on the filing cabinet. Test what happens when the cabinet is closed:

```bash
docker compose stop db
```

Submit a new work order in the browser. The page should say `Could not save the work order.` Now
open Kibana (<http://localhost:5601>) and search for `500` or `Error` to find the front desk's notes about the
failure. Reopen the cabinet:

```bash
docker compose start db
```

Submit the work order again. It works.

## Rebuild after changing the code

Changed `app/main.py`, `Dockerfile` or a file under `app/static/`? Rebuild the front desk:

```bash
docker compose up --build -d
```

## Service addresses and ports

| Service | Address from your computer | What it is |
|---|---|---|
| Application | <http://localhost:9000> | Web page and work order API |
| API health | <http://localhost:9000/healthz> | Health check |
| Kibana | <http://localhost:5601> | Search the logs |
| Elasticsearch | <http://localhost:9200> | Log storage (for the curious) |
| RabbitMQ UI | <http://localhost:15672> | Announcement board (`guest` / `guest`) |
| RabbitMQ messages | `localhost:5672` | Messaging port (not a web page) |
| PostgreSQL | `localhost:5433` | Filing cabinet (user `ifs`, password `ifs`, database `ifsdb`) |
| Logstash | `localhost:12201/udp` | Receives the log notes (not a web page) |

PostgreSQL, RabbitMQ messages and Logstash are not websites. Opening their ports in a browser shows nothing.

## Project structure

```text
docker-lab/
├── app/
│   ├── main.py                    # The front desk: API code
│   ├── requirements.txt           # Python packages it needs
│   ├── static/images/             # IFS logo and NSBM tab icon
│   └── templates/index.html       # The web page
├── logstash/pipeline/
│   └── logstash.conf              # Where log notes go
├── Dockerfile                     # The recipe for the front desk
├── docker-compose.yml             # The plan for all six helpers
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
Another program uses one of the ports, such as 9000 or 5601. Stop that program, or change the left-hand
number in `docker-compose.yml`. For example, `"9001:9000"` makes the app open at <http://localhost:9001>.

**Kibana page does not open yet**
Kibana starts slowly. Wait a minute, then check:

```bash
docker compose ps
docker compose logs kibana
docker compose logs elasticsearch
```

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

**Logs do not reach Kibana**
The API sends its logs to `host.docker.internal:12201`. Docker Desktop provides that name. On Linux or WSL
with Docker Engine, the name may not exist. Change `gelf-address` in `docker-compose.yml` to an address the
Docker host can reach, such as your host's bridge IP, then run:

```bash
docker compose up --build -d --force-recreate api
```

**Something is stuck**
Look at one helper's logs (not `api`, which sends its logs to Kibana):

```bash
docker compose logs db
docker compose logs mq
docker compose logs logstash
docker compose logs elasticsearch
docker compose logs kibana
```

The `api` container sends its logs to Kibana with the GELF logging driver. That driver does not keep logs
on your computer, so `docker compose logs api` cannot show them. Look in Kibana instead.

## Clear the classroom data only

Delete only the log indices, while everything keeps running:

```bash
curl -X DELETE "http://localhost:9200/nsbm-logs-*"
```

> This lab uses simple passwords and turns off Elasticsearch security so it is easy to learn with.
> Do not deploy this configuration to production or expose it to the internet.

## Next

When you are comfortable with Compose, move on to the [Kubernetes lab](../k8s-lab/README.md).
