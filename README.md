# Emerging Technologies: Cloud and DevOps Labs

Hands-on labs for learning **Docker** and **Kubernetes**, built for students who are new to them.
Each lab is a short story with real commands, so you can see what each step does and why.

Based on the hands-on DevOps and cloud workshop run by IFS for the NSBM FIT Programme.

## Where to start

Do the labs in this order:

1. **[Docker Lab](docker-lab/README.md)**: run a six-service work order app with Docker Compose.
   Start here if you have never used Docker.
2. **[Kubernetes Lab](k8s-lab/README.md)**: run a practice cluster on your computer, then deploy, scale, configure,
   store data, check health and package apps in six labs.

## What you need

| For | You need |
|---|---|
| Docker Lab | Docker Desktop (Windows or Mac), or Docker Engine (Linux or WSL), with Docker Compose |
| Kubernetes Lab | Docker, plus one of: VS Code with Dev Containers, GitHub Codespaces, or Linux or WSL with `kind`, `kubectl` and Helm |

Both labs need a computer with at least 4 GB RAM free and several GB of disk space.

> **Download on Wi-Fi.** The first start of each lab downloads several gigabytes of container images.
> On mobile data this uses a lot of your data plan, so start the first download on Wi-Fi.
> After that, the images stay on your computer.

## Repository layout

```text
.
├── docker-lab/                 # Docker Compose lab: a work order app
│   └── README.md               # Start here
└── k8s-lab/                    # Kubernetes lab: a practice cluster
    ├── README.md               # Setup options and the lab map
    ├── kind-config.yaml        # The cluster's shape (1 control plane, 2 workers)
    ├── scripts/                # Create, reset and set up the cluster
    └── labs/                   # Six labs, each with a README and verify.sh
```

## Credits

The IFS and NSBM logos belong to their owners. They appear here only so the labs look like the workshop.
Use them only for learning, and replace them with the versions your organisation supplies.
