# Lab 01: Your first Deployment

## The story

You run the website for a small online shop. The website is a simple page served by **nginx**, a
web server. Customers must always be able to reach it.

You could start one copy by hand. But if that copy crashes at 2 AM, the shop is offline until someone wakes
up. So you write a **Deployment**. It says, in effect: "Keep three copies of this website running, always."

Each copy is a **pod**, one worker. If a worker stops, the Deployment hires a replacement straight away.

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

- `replicas: 3`, meaning three pods.
- `image: nginx:1.27`, the recipe each pod is cooked from.
- `containerPort: 80`, the door the web server listens on.

### Step 2: Send the plan to the cluster

```bash
kubectl apply -f deployment.yaml
```

Expected output: `deployment.apps/web created`.

`kubectl apply` means "make the cluster match this file." Run it again later and nothing changes, because the
cluster already matches.

### Step 3: Watch the workers start

```bash
kubectl get pods -o wide -w
```

`-o wide` adds extra columns. `-w` keeps the list updating. You should see three pods move from
`ContainerCreating` to `Running`. The `NODE` column shows which computer each pod is on.

Press `Ctrl+C` to stop watching.

**Question:** Which nodes did the pods land on? Why do you think Kubernetes chose those nodes?
(Hint: Kubernetes spreads pods across the workers so one computer failing does not take the whole site down.)

### Step 4: Delete a worker

Copy the name of one pod from `kubectl get pods`, then delete it:

```bash
kubectl delete pod <pod-name>
```

Run `kubectl get pods` straight away. You should see three pods again. One has a new name.

**Question:** What happened, and why? The Deployment's job is to keep three pods running, so it started a
replacement. The pod you deleted is gone for good. Only the Deployment is permanent.

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

**Question:** Did the website go down? Usually not. Kubernetes replaces pods gradually, so the old working
pods keep serving customers while the broken one waits.

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

Expected output: `PASS: web has 3 ready replicas`.

## Clean up

Leave the Deployment running for lab 02. It needs `web`.

## If something goes wrong

- **`verify.sh` says FAIL:** run `kubectl get deploy web` and `kubectl get pods`. Look for a pod that is not
  `Running`, then run `kubectl describe pod <name>` to see why.
- **Stuck on `ContainerCreating` for minutes:** the image is still downloading. Check with
  `kubectl describe pod <name>`.
- **Something is badly broken:** `bash ../../scripts/cluster-reset.sh` gives you a clean cluster. Then start again from step 1.
