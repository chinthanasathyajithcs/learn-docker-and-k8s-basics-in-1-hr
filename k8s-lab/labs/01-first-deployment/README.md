# Lab 01: Your first Deployment

## The story

The lunch rush in the Docker lab showed the problem: one stall with one cook cannot keep up, and when the cook
collapses, nobody reopens the stall. So Sam stops cooking and becomes the **manager**.

Sam opens three identical stalls and writes one instruction on a clipboard: "Keep three stalls running,
always." In Kubernetes, that instruction is a **Deployment**. Each running copy is a **pod**, one cook at one
stall. If a cook leaves, the Deployment brings in a new cook straight away.

Each stall here runs **nginx**, a small web server, so the cluster stays light. In lab 03 you put Sam's sign
on it.

## What you will learn

- How to describe what you want in a YAML file and send it to the cluster with `kubectl apply`.
- What a pod is, and that Kubernetes decides which computer (node) each pod runs on.
- How Kubernetes repairs itself when a pod is deleted.
- How to find out why something failed, using `kubectl describe`.

## Before you start

Your cluster must be running. Check it:

```bash
kubectl get nodes
```

You should see three nodes, all with `STATUS` `Ready`: one `control-plane` and two workers.

## Steps

### Step 1: Go to the lab folder

```bash
cd labs/01-first-deployment
```

Open `deployment.yaml` and read it. It asks for:

- `name: stall`, the name of the Deployment.
- `replicas: 3`, meaning three pods: three cooks.
- `image: nginx:1.27`, the recipe card each pod is packed from.
- `containerPort: 80`, the door the web server listens on.

### Step 2: Hand the clipboard to the cluster

```bash
kubectl apply -f deployment.yaml
```

Expected output: `deployment.apps/stall created`.

`kubectl apply` means "make the cluster match this file." Run it again later and nothing changes, because the
cluster already matches.

### Step 3: Watch the cooks start

```bash
kubectl get pods -o wide -w
```

`-o wide` adds extra columns. `-w` keeps the list updating. You should see three pods move from
`ContainerCreating` to `Running`. The `NODE` column shows which computer each pod is on.

Press `Ctrl+C` to stop watching.

**Question:** Which nodes did the pods land on? Why do you think Kubernetes chose those nodes?
(Hint: Kubernetes spreads pods across the workers so one computer failing does not close every stall.)

### Step 4: A cook leaves

Copy the name of one pod from `kubectl get pods`, then delete it:

```bash
kubectl delete pod <pod-name>
```

Run `kubectl get pods` straight away. You should see three pods again. One has a new name.

**Question:** What happened, and why? The Deployment's job is to keep three cooks working, so it brought in a
replacement. The pod you deleted is gone for good. Only the Deployment, Sam's clipboard, is permanent.

### Step 5: Break it on purpose

Open `deployment.yaml` and change the image line to a version that does not exist:

```yaml
          image: nginx:doesnotexist
```

Apply it again:

```bash
kubectl apply -f deployment.yaml
kubectl get pods
```

You will see a new pod stuck in `ErrImagePull` or `ImagePullBackOff`. Find out why:

```bash
kubectl describe pod <stuck-pod-name>
```

Scroll to the **Events** section at the bottom. It says the image could not be found.

**Question:** Did the stalls close? Usually not. Kubernetes replaces pods gradually, so the old cooks keep
serving customers while the new one waits for a recipe card that does not exist.

### Step 6: Fix it

Change the image back to `nginx:1.27` in `deployment.yaml`, then apply:

```bash
kubectl apply -f deployment.yaml
kubectl get pods
```

After a short wait, all three pods are `Running` and `READY 1/1`, and the broken pod is gone.

### Step 7: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: stall has 3 ready cooks`.

## Clean up

Leave the Deployment running for lab 02. It needs `stall`.

## If something goes wrong

- **`verify.sh` says FAIL:** run `kubectl get deploy stall` and `kubectl get pods`. Look for a pod that is not
  `Running`, then run `kubectl describe pod <name>` to see why.
- **Stuck on `ContainerCreating` for minutes:** the image is still downloading. Check with
  `kubectl describe pod <name>`.
- **Something is badly broken:** `bash ../../scripts/cluster-reset.sh` gives you a clean cluster. Then start again from step 1.
