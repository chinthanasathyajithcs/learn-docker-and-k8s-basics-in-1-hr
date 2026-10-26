# Learn Docker and Kubernetes Basics in 1 Hour

Hands-on labs for students who are new to **Docker** and **Kubernetes**. Each lab is a short story with real
commands, so you see what each step does and why.

Based on the hands-on DevOps and cloud workshop run by IFS for the NSBM FIT Programme.

## The story

Sam runs one burger stall at a campus fair. Step by step, the stall grows into a chain, and each step teaches
one idea.

| | In the story | You learn | Lab |
|---|---|---|---|
| 1 | One stall on a quiet morning | Why an app breaks on another computer | [Docker](docker-lab/README.md), steps 1 and 2 |
| 2 | The recipe card and the boxes | Images and containers | [Docker](docker-lab/README.md), step 3 |
| 3 | The kitchen team | Running several containers together (Compose) | [Docker](docker-lab/README.md), steps 4 to 9 |
| 4 | The lunch rush | What one computer cannot do | [Docker](docker-lab/README.md), steps 10 to 12 |
| 5 | Three stalls and a manager | Deployments and self-healing | [Kubernetes 01](k8s-lab/labs/01-first-deployment/README.md) |
| 6 | Five stalls, one front desk | Services and scaling | [Kubernetes 02](k8s-lab/labs/02-services-and-scaling/README.md) |
| 7 | The notice board, the safe and the locker | Settings, secrets and storage | [Kubernetes 03](k8s-lab/labs/03-config-and-branding/README.md) and [04](k8s-lab/labs/04-persistent-storage/README.md) |
| 8 | The morning check-in | Health checks and memory limits | [Kubernetes 05](k8s-lab/labs/05-health-and-self-healing/README.md) |
| 9 | One recipe card, different settings | Helm | [Kubernetes 06](k8s-lab/labs/06-helm/README.md) |

## Start here

- **One hour:** the [Docker lab](docker-lab/README.md), then Kubernetes labs 01 and 02.
- **Everything:** the Docker lab, then all six [Kubernetes labs](k8s-lab/README.md). About 3 hours.

New to Docker? Start with the Docker lab.

## What you need

- **Docker**: Docker Desktop on Windows or Mac, or Docker Engine on Linux or WSL.
- **For Kubernetes**, one of: VS Code with Dev Containers, GitHub Codespaces, or `kind`, `kubectl` and Helm on
  Linux or WSL. The [Kubernetes lab](k8s-lab/README.md) explains each option.
- A computer with 4 GB of free memory and 10 GB of free disk space.

## Downloads

The first time you start each lab, it downloads what it needs. After that, everything stays on your computer.

- Docker lab: about 0.3 GB.
- Kubernetes lab: about 0.5 GB, plus roughly 1 GB more if you use the Dev Container or Codespaces.

> **Use Wi-Fi.** These downloads use a lot of mobile data. A classmate can also give you the files (see below).

### Offline setup

One person downloads everything on Wi-Fi and saves it to a file. Everyone else copies the file, for example
from a USB drive, and loads it without internet.

<details>
<summary>Show the commands</summary>

**Docker lab.** The person on Wi-Fi runs the lab once (`docker compose up --build -d` in `docker-lab/`), then:

```bash
docker save postgres:16-alpine rabbitmq:3.13-management \
  docker-lab-cashier docker-lab-notebook | gzip > docker-lab-images.tar.gz
```

Everyone else loads the file, then starts the lab **without** `--build`, so nothing is rebuilt or downloaded:

```bash
docker load < docker-lab-images.tar.gz
cd docker-lab
docker compose up -d
```

**Kubernetes lab.** The cluster itself (about 440 MB) still downloads once per computer. The images the labs
use inside it can come from a file. The person on Wi-Fi runs:

```bash
for img in nginx:1.27 nginx:1.27-alpine busybox:1.36 polinux/stress:1.0.4; do docker pull "$img"; done
docker save nginx:1.27 nginx:1.27-alpine busybox:1.36 polinux/stress:1.0.4 | gzip > k8s-lab-images.tar.gz
```

Everyone else loads the file and copies the images into the cluster after it starts:

```bash
docker load < k8s-lab-images.tar.gz
kind load docker-image nginx:1.27 nginx:1.27-alpine busybox:1.36 polinux/stress:1.0.4 --name lab
```

</details>

## Learn with an AI assistant

Coding assistants such as Claude Code, GitHub Copilot and Codex read [`AGENTS.md`](AGENTS.md) and act as your
tutor: they explain each idea before the command and ask you a short question after each step.

<details>
<summary>Using a chat assistant instead? Paste this first</summary>

```text
I am a beginner doing the Docker and Kubernetes labs at
https://github.com/chinthanasathyajithcs/learn-docker-and-k8s-basics-in-1-hr.
Act as my tutor. Explain the idea behind each step in plain words before any command,
use simple real-world analogies, give me one step at a time, and ask me a short
question afterwards to check that I understood. When I paste an error, explain what
it means before telling me the fix.
```

</details>

## Licence

The labs are released under the [MIT License](LICENSE).
