# Learn Docker and Kubernetes Basics in 1 Hour

Hands-on labs for learning **Docker** and **Kubernetes**, built for students who are new to them.
Each lab is a short story with real commands, so you can see what each step does and why.

Based on the hands-on DevOps and cloud workshop run by IFS for the NSBM FIT Programme.

## What you will learn

### Docker Lab

| Topic | What it means | Where |
|---|---|---|
| Images and containers | A recipe, and a meal cooked from it | Steps 3 and 4 |
| Building your own image | Writing a `Dockerfile`, including a two-stage build | Step 3, `Dockerfile` |
| Running many services together | One `docker-compose.yml` starts six services | Steps 2 to 4 |
| Container networking | Services find each other by name, such as `db` | Steps 6 and 7 |
| Ports | Opening a container's door to your computer | Step 5 |
| Health checks and start-up order | Start the API only after the database is ready | Step 4 |
| Configuration with environment variables | Same image, different settings | `docker-compose.yml` |
| Volumes | Data that survives when containers are deleted | Step 10 |
| Message queues | One service announces an event, another reads it (RabbitMQ) | Step 8 |
| Centralised logging | Collect, store and search logs (Logstash, Elasticsearch, Kibana) | Step 9 |
| Debugging a failure | What happens when a service the app depends on stops | Challenge |

### Kubernetes Lab

| Topic | What it means | Lab |
|---|---|---|
| Clusters and nodes | A group of computers that Kubernetes manages | Setup |
| Deployments and pods | "Keep this many copies running" | [01](k8s-lab/labs/01-first-deployment/README.md) |
| Self-healing | Replacing pods that are deleted or crash | [01](k8s-lab/labs/01-first-deployment/README.md), [05](k8s-lab/labs/05-health-and-self-healing/README.md) |
| Debugging with `describe` and `logs` | Finding out why a pod failed | [01](k8s-lab/labs/01-first-deployment/README.md), [05](k8s-lab/labs/05-health-and-self-healing/README.md) |
| Services | One stable address in front of many pods | [02](k8s-lab/labs/02-services-and-scaling/README.md) |
| Scaling | More copies for busy times | [02](k8s-lab/labs/02-services-and-scaling/README.md) |
| Rolling updates and rollbacks | New versions without downtime, and a way back | [02](k8s-lab/labs/02-services-and-scaling/README.md), [06](k8s-lab/labs/06-helm/README.md) |
| ConfigMaps | Settings and files kept outside the image | [03](k8s-lab/labs/03-config-and-branding/README.md) |
| Secrets | Passwords, and why base64 is not encryption | [03](k8s-lab/labs/03-config-and-branding/README.md) |
| Persistent storage | Volumes that outlive pods | [04](k8s-lab/labs/04-persistent-storage/README.md) |
| Readiness and liveness probes | "Ready for visitors?" and "Still alive?" | [05](k8s-lab/labs/05-health-and-self-healing/README.md) |
| Resource limits | Memory limits, and what `OOMKilled` means | [05](k8s-lab/labs/05-health-and-self-healing/README.md) |
| Helm | Packaged, configurable apps with history | [06](k8s-lab/labs/06-helm/README.md) |

## Choose your path

| Path | What to do | Time |
|---|---|---|
| **Quick (1 hour)** | [Docker Lab](docker-lab/README.md), then Kubernetes labs [01](k8s-lab/labs/01-first-deployment/README.md) and [02](k8s-lab/labs/02-services-and-scaling/README.md) | About 1 hour |
| **Full** | The Docker Lab, then all six [Kubernetes labs](k8s-lab/README.md) | About 3 hours |

Start with the Docker Lab if you have never used Docker.

## Learn with an AI assistant

This repo includes tutor instructions for AI assistants in [`AGENTS.md`](AGENTS.md). Coding assistants that read
that file, such as Claude Code, GitHub Copilot and Codex, will explain each idea before the command, ask you check
questions, and warn you before large downloads.

Using a chat assistant instead? Paste this at the start of the chat:

```text
I am a beginner doing the Docker and Kubernetes labs at
https://github.com/chinthanasathyajithcs/learn-docker-and-k8s-basics-in-1-hr.
Act as my tutor. Explain the idea behind each step in plain words before any command,
use simple real-world analogies, give me one step at a time, and ask me a short
question afterwards to check that I understood. When I paste an error, explain what
it means before telling me the fix.
```

## What you need

| For | You need |
|---|---|
| Docker Lab | Docker Desktop (Windows or Mac), or Docker Engine (Linux or WSL), with Docker Compose |
| Kubernetes Lab | Docker, plus one of: VS Code with Dev Containers, GitHub Codespaces, or Linux or WSL with `kind`, `kubectl` and Helm |

Both labs need a computer with at least 4 GB RAM free and about 10 GB of free disk space.

## Downloads

Images are downloaded from online registries, mostly [Docker Hub](https://hub.docker.com/), the first time you
use them. After that, they stay on your computer and later starts need no download.

| Lab | Download | Biggest parts |
|---|---|---|
| Docker Lab | About 1.8 GB | Elasticsearch, Logstash and Kibana, about 1.55 GB together |
| Kubernetes Lab | About 0.5 GB | The kind node image, about 440 MB |
| Dev Container (Kubernetes options A and B) | Roughly 1 GB more | The container image and its tools |

> **Download on Wi-Fi.** These downloads use a lot of mobile data. Do the first start on Wi-Fi, or get the
> images from a classmate as a file (see below).

### Offline setup

One person downloads the images on Wi-Fi and saves them to a file. Everyone else copies the file, for example
from a USB drive, and loads it. No internet is needed.

**Docker Lab.** The person on Wi-Fi runs the lab once (`docker compose up --build -d` in `docker-lab/`), then:

```bash
docker save postgres:16-alpine rabbitmq:3.13-management elasticsearch:8.15.3 \
  logstash:8.15.3 kibana:8.15.3 docker-lab-api | gzip > docker-lab-images.tar.gz
```

Everyone else loads the file, then starts the lab **without** `--build`, so nothing is rebuilt or downloaded:

```bash
docker load < docker-lab-images.tar.gz
cd docker-lab
docker compose up -d
```

**Kubernetes Lab images.** The kind node image (about 440 MB) still downloads once per computer. The images
the labs run inside the cluster can come from a file. The person on Wi-Fi runs:

```bash
for img in nginx:1.27 nginx:1.27-alpine busybox:1.36 polinux/stress:1.0.4; do docker pull "$img"; done
docker save nginx:1.27 nginx:1.27-alpine busybox:1.36 polinux/stress:1.0.4 | gzip > k8s-lab-images.tar.gz
```

Everyone else loads the file and copies the images into the cluster after it starts:

```bash
docker load < k8s-lab-images.tar.gz
kind load docker-image nginx:1.27 nginx:1.27-alpine busybox:1.36 polinux/stress:1.0.4 --name lab
```

## Repository layout

```text
.
├── AGENTS.md                   # Tutor instructions for AI assistants
├── docker-lab/                 # Docker Compose lab: a work order app
│   └── README.md               # Start here
└── k8s-lab/                    # Kubernetes lab: a practice cluster
    ├── README.md               # Setup options and the lab map
    ├── kind-config.yaml        # The cluster's shape (1 control plane, 2 workers)
    ├── scripts/                # Create, reset and set up the cluster
    └── labs/                   # Six labs, each with a README and verify.sh
```

## Credits and licence

The labs are released under the [MIT License](LICENSE).

The IFS and NSBM logos belong to their owners. They appear here only so the labs look like the workshop.
Use them only for learning, and replace them with the versions your organisation supplies.
