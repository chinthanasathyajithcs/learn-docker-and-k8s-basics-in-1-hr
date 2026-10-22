# Lab 02: Services and scaling

## The story

The shop's website is running on three workers from lab 01. But customers do not know which worker is
which, and they should not have to. Each worker has its own address inside the cluster, and those
addresses can change when a worker is replaced.

You need a **front desk**. A **Service** is that front desk: one stable address. Visitors go to the Service, and
the Service sends each visitor to a worker that is ready.

Then lunchtime arrives and the shop gets busy. You hire two more workers (**scaling**). Later you want to
publish a new version of the website without closing the shop (a **rolling update**). If the new version
turns out to be broken, you go back to the old one (a **rollback**).

## What you will learn

- How a Service gives pods one stable address.
- How to scale a Deployment up and down.
- How rolling updates work, and how to roll back.

## Before you start

Lab 01 must be finished, because this lab uses the `web` Deployment. Check that it exists:

```bash
kubectl get deploy web
```

You should see `READY 3/3`. If not, do lab 01 first.

## Steps

### Step 1: Hire a front desk

```bash
cd labs/02-services-and-scaling
kubectl apply -f service.yaml
kubectl get svc web
```

`svc` is short for Service. Look at the `PORT(S)` column: `80:30080/TCP`. The `30080` is the door the cluster
opens on each node. The cluster setup links that door to port `8080` on your computer.

### Step 2: Visit the shop

Open <http://localhost:8080> in your browser. You should see the nginx page titled **Welcome to nginx!**

Refresh a few times. Every visit goes through the same front desk, which picks a ready worker each time.

> If the page does not open, check that the Service exists (step 1) and that nothing else uses port 8080.

### Step 3: See who is behind the desk

```bash
kubectl get endpoints web
```

The `ENDPOINTS` column lists the IP addresses of the three ready pods. These are the workers the front desk
can send visitors to.

### Step 4: Scale up for lunch

```bash
kubectl scale deploy web --replicas=5
kubectl get endpoints web
```

Run `kubectl get endpoints web` again after a few seconds. You should see five addresses now.

**Question:** Did the front desk's address change? No. Only the list of workers behind it grew.

Scale back to three before you move on, because lab 01's check expects three:

```bash
kubectl scale deploy web --replicas=3
```

### Step 5: Publish a new version without closing

Switch the website from `nginx:1.27` to `nginx:1.27-alpine`, a smaller build of the same version:

```bash
kubectl set image deploy/web nginx=nginx:1.27-alpine
kubectl rollout status deploy/web
```

`rollout status` waits until the update finishes. Watch the pods with `kubectl get pods -w` (press `Ctrl+C`
to stop). New pods start, and old pods are removed only after the new ones are ready.

**Question:** Did any visitor see a broken site during the update? The old pods kept serving until the new
ones were ready.

### Step 6: Roll back

Imagine the new version has a bug. Go back to the previous version:

```bash
kubectl rollout history deploy/web
kubectl rollout undo deploy/web
kubectl rollout status deploy/web
```

`rollout history` lists the versions Kubernetes remembers. `rollout undo` returns to the one before.

Check the image again:

```bash
kubectl get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```

It should print `nginx:1.27`.

### Step 7: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: service reachable on :8080`.

## Clean up

Leave the Service and the Deployment in place. Labs 03 and later do not need them, but lab 01's check does.

## If something goes wrong

- **Port 8080 does not respond:** run `kubectl get svc web`. The `PORT(S)` column must show `30080`. If
  the cluster was built without the port mapping, run `bash ../../scripts/cluster-reset.sh`.
- **`kubectl get endpoints` shows `<none>`:** no pods are ready. Run `kubectl get pods` and follow lab 01's
  troubleshooting steps.
