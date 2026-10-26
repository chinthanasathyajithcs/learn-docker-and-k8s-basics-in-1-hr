# Lab 02: Services and scaling

## The story

Sam's three stalls from lab 01 are open. But customers do not know which stall is which, and they should not
have to. Each cook has their own address inside the cluster, and that address changes when a cook is replaced.

Sam needs a **front desk**. A **Service** is that front desk: one stable address. Customers go to the front
desk, and it sends each one to a stall whose cook is ready.

Then lunchtime arrives and the fair gets busy. Sam brings in two more cooks (**scaling**). Later Sam wants to
change something in every stall without closing any of them (a **rolling update**). If the change turns out
badly, Sam goes back to how it was (a **rollback**).

## What you will learn

- How a Service gives pods one stable address.
- How to scale a Deployment up and down.
- How rolling updates work, and how to roll back.

## Before you start

Lab 01 must be finished, because this lab uses the `stall` Deployment. Check that it exists:

```bash
kubectl get deploy stall
```

You should see `READY 3/3`. If not, do lab 01 first.

## Steps

### Step 1: Open the front desk

```bash
cd labs/02-services-and-scaling
kubectl apply -f service.yaml
kubectl get svc front-desk
```

`svc` is short for Service. Look at the `PORT(S)` column: `80:30080/TCP`. The `30080` is the door the cluster
opens on each node. The cluster setup links that door to port `8080` on your computer.

### Step 2: Visit the stalls

Open <http://localhost:8080> in your browser. You should see the nginx page titled **Welcome to nginx!**

Refresh a few times. Every visit goes through the same front desk, which picks a ready cook each time.

> If the page does not open, check that the Service exists (step 1) and that nothing else uses port 8080.

### Step 3: See who is behind the desk

```bash
kubectl get endpoints front-desk
```

The `ENDPOINTS` column lists the addresses of the three ready pods. These are the cooks the front desk can send
customers to.

### Step 4: Scale up for lunch

```bash
kubectl scale deploy stall --replicas=5
kubectl get endpoints front-desk
```

Run `kubectl get endpoints front-desk` again after a few seconds. You should see five cooks now: kubectl
lists three addresses and then `+ 2 more...`.

**Question:** Did the front desk's address change? No. Only the list of cooks behind it grew.

Scale back to three before you move on, because lab 01's check expects three:

```bash
kubectl scale deploy stall --replicas=3
```

### Step 5: Change every stall without closing

Switch the stalls from `nginx:1.27` to `nginx:1.27-alpine`, a smaller build of the same version:

```bash
kubectl set image deploy/stall nginx=nginx:1.27-alpine
kubectl rollout status deploy/stall
```

`rollout status` waits until the update finishes. Watch the pods with `kubectl get pods -w` (press `Ctrl+C`
to stop). New cooks start, and old cooks leave only after the new ones are ready.

**Question:** Did any customer find a closed stall during the update? The old cooks kept serving until the
new ones were ready.

### Step 6: Roll back

Imagine the change was a mistake. Go back to the previous version:

```bash
kubectl rollout history deploy/stall
kubectl rollout undo deploy/stall
kubectl rollout status deploy/stall
```

`rollout history` lists the versions Kubernetes remembers. `rollout undo` returns to the one before.

Check the image again:

```bash
kubectl get deploy stall -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```

It should print `nginx:1.27`.

### Step 7: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: front desk reachable on :8080`.

## Clean up

Leave the front desk and the stalls in place. Labs 03 and later do not need them, but lab 01's check does.

## If something goes wrong

- **Port 8080 does not respond:** run `kubectl get svc front-desk`. The `PORT(S)` column must show `30080`. If
  the cluster was built without the port mapping, run `bash ../../scripts/cluster-reset.sh`.
- **`kubectl get endpoints` shows `<none>`:** no pods are ready. Run `kubectl get pods` and follow lab 01's
  troubleshooting steps.
