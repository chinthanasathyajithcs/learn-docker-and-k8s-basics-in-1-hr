# Kubernetes Lab

In the Docker lab, Sam's stall ran on one computer. The lunch rush showed its limits: you could not start more
cashiers on the same door, and when the cashier collapsed, nobody reopened the stall.

**Kubernetes** fixes that. Sam stops cooking and becomes the manager. You describe what you want ("keep three
stalls open"), and Kubernetes keeps making reality match your description: it opens the stalls, replaces any
cook who leaves, and sends customers to cooks who are ready.

This lab gives you a small practice cluster on your own computer: the fairground. It has one control-plane
computer and two worker computers, all made of Docker containers. Nothing here touches a real server, and you
can throw the whole cluster away and start again.

## Choose how to start

Pick **one** option. Option A is the easiest for most students.

### Option A: Dev Container in VS Code (recommended)

Needs Docker Desktop with at least 2 CPUs and 4 GB RAM allocated, plus VS Code.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
2. Install [VS Code](https://code.visualstudio.com/) and the **Dev Containers** extension.
3. Clone this repository and open the `k8s-lab` folder in VS Code.
4. Choose **Reopen in Container** when VS Code asks.
5. Wait for the terminal to print the node list. Check it yourself:

   ```bash
   kubectl get nodes
   ```

### Option B: GitHub Codespaces (no installs)

On the repository's GitHub page, select **Code > Codespaces > Create codespace on main**. The container opens in
your browser. Codespaces has a free monthly quota, and the first start takes several minutes.

### Option C: Native Linux or WSL (advanced)

Use this only if you already know Docker. You need Docker, [kind](https://kind.sigs.k8s.io/), `kubectl`
and [Helm](https://helm.sh/docs/intro/install/). Then run:

```bash
cd k8s-lab
bash scripts/cluster-up.sh
kubectl get nodes
```

> **Mobile data warning:** the cluster and lab images are about 0.5 GB. Options A and B also download the
> dev container image and its tools, roughly 1 GB more. Do this on Wi-Fi, ideally before the session.

## Words you need first

| Word | Plain English |
|---|---|
| **Cluster** | The whole group of computers that Kubernetes manages: the fairground. |
| **Node** | One computer in the cluster. Here, each node is a Docker container. |
| **Pod** | The smallest unit that runs. It holds one or more containers. Think of a pod as one cook at one stall. |
| **Deployment** | Sam's clipboard: "Keep this many pods of this app running." If a cook leaves, the Deployment brings in a new one. |
| **Service** | The front desk. Customers go to the Service, and the Service sends them to a cook who is ready. |
| **ConfigMap / Secret** | The notice board and the safe: settings and passwords kept outside the app, so the same app can run in different places. |
| **PersistentVolumeClaim** | A request for a locker: storage that outlives a pod. |
| **Probe** | A health check Kubernetes runs on a pod, like Sam's morning check-in. |
| **Helm chart** | A recipe card for a whole stall, with adjustable settings. |

## The labs

Do them in order. Labs 03 to 06 are independent of each other after lab 02.

| Lab | Story | You will learn | Time |
|---|---|---|---|
| [01 First Deployment](labs/01-first-deployment/README.md) | Sam becomes the manager of three stalls | Deployments, pods, self-healing | 15 min |
| [02 Services and Scaling](labs/02-services-and-scaling/README.md) | Open a front desk and handle the lunch rush | Services, scaling, safe updates and rollbacks | 20 min |
| [03 Config and Branding](labs/03-config-and-branding/README.md) | Pin the sign to the notice board and lock the secret sauce in the safe | ConfigMaps, Secrets | 25 min |
| [04 Persistent Storage](labs/04-persistent-storage/README.md) | Keep the notebook in a locker when cooks change | PersistentVolumeClaims | 20 min |
| [05 Health and Self-Healing](labs/05-health-and-self-healing/README.md) | The morning check-in: is every cook ready? | Probes, crash loops, memory limits | 30 min |
| [06 Helm](labs/06-helm/README.md) | One recipe card, a small stall and a big stall | Charts, releases, upgrades, rollbacks | 25 min |

Each lab folder has a `README.md` with the steps and a `verify.sh` script. When you finish a lab, run
its `verify.sh` to check your work:

```bash
bash labs/01-first-deployment/verify.sh
```

## Useful commands

| Command | What it does |
|---|---|
| `kubectl get nodes` | Shows the computers in the cluster |
| `kubectl get pods` | Shows the running cooks (pods) |
| `k9s` | A full-screen dashboard for the cluster (press `:` then type `pods`, and `Esc` to go back) |
| `k` | A short name for `kubectl` (Option A and B only) |
| `bash scripts/cluster-reset.sh` | Deletes the cluster and creates a fresh one |

## Reset the cluster

Broke something you cannot fix? Start again from a clean cluster:

```bash
bash scripts/cluster-reset.sh
```

Then start from lab 01. The reset removes everything you created, so you will need to redo the earlier labs.

## Troubleshooting

**`Cannot connect to the Docker daemon`**
Start Docker Desktop, or on Linux or WSL start the Docker service. Then reopen the container or run
`bash scripts/cluster-up.sh` again.

**`kubectl get nodes` shows `NotReady` or no nodes**
Wait two minutes. A new cluster needs time. If it still fails, run `bash scripts/cluster-reset.sh`.

**`port is already allocated` on 8080 or 8081**
Labs 02 and 03 use host ports 8080 and 8081. Stop whatever else uses them. On Windows, check with
`netstat -ano | findstr :8080`.

**`accessing specified distro mount service ... ubuntu.sock` on container start (Windows with WSL Ubuntu)**
In VS Code settings, untick `dev.containers.mountWaylandSocket`, then reopen in the container.

**Pods stay in `ContainerCreating` or `ImagePullBackOff` for a long time**
The cluster is downloading images. On a slow connection this can take many minutes. Check progress with
`kubectl describe pod <name>` and look at the Events section.

## For instructors

- Students on Windows need WSL2 enabled in Docker Desktop (the default).
- Apple Silicon and x86 both work. The install script picks the right architecture.
- Ask students to finish the setup on Wi-Fi before the session.
- Lab 03's logo is `labs/03-config-and-branding/assets/burger.png`. Replace it with your own if you like,
  keeping the name and keeping the file under 1 MB.
- To add a lab, create a folder under `labs/` with a `README.md` and a `verify.sh`.
