# Lab 05: Probes, limits and self-healing

## The story

The shop has three workers. Kubernetes checks on them all day, using two different questions:

- **Readiness: "Are you ready for customers?"** A worker that answers "no" is kept out of the front desk's list.
  It is not sent home. It may recover on its own.
- **Liveness: "Are you still alive?"** A worker that answers "no" is restarted.

Some workers are also given a **memory limit**, like a shopping basket with a maximum weight. A worker that
carries more than its limit is removed.

Finally, some workers are broken in ways you must fix yourself: a missing key that stops them starting, and a
basket that is too small for the job.

## What you will learn

- The difference between readiness and liveness probes, and what each one does.
- How Kubernetes restarts a crashing container, and how to find out why it crashed.
- How memory limits work, and how to read the reason a pod was stopped.

## Before you start

The cluster must be running. Lab 05 does not depend on earlier labs.

## Steps

### Step 1: Open the shop with three workers

```bash
cd labs/05-health-and-self-healing
kubectl apply -f healthy.yaml
kubectl get pods -l app=healthy
```

Wait until all three pods show `READY 1/1`. `healthy.yaml` also contains a Service named `healthy`, which is
the front desk for these workers.

### Step 2: Readiness: take a worker off the front desk

Pick one pod and delete its web page, so nginx has nothing to show:

```bash
POD=$(kubectl get pod -l app=healthy -o name | head -1)
kubectl exec $POD -- rm /usr/share/nginx/html/index.html
kubectl get pods -l app=healthy -w
```

Press `Ctrl+C` after about 15 seconds. The broken pod is still `Running`, but `READY` shows `0/1`.

Check the front desk's list:

```bash
kubectl get endpoints healthy
```

The broken pod's address is gone. Visitors now go only to the two healthy workers.

**Question:** Why was the broken pod not restarted? The readiness probe only decides whether a pod receives
visitors. A pod that is not ready is left alone, in case it recovers. Restarting it would not help, because
the probe checks the page, and a restart would not put the file back.

**Fix it:** delete the broken pod, and the Deployment will hire a fresh one:

```bash
kubectl delete pod $POD
kubectl get pods -l app=healthy
```

Wait until all three pods show `READY 1/1`.

### Step 3: Liveness: a worker that dies is restarted

Stop nginx inside one pod:

```bash
POD=$(kubectl get pod -l app=healthy -o name | head -1)
kubectl exec $POD -- nginx -s stop
kubectl get pods -l app=healthy
```

Look at the `RESTARTS` column. It goes up to `1`. When nginx stopped, the container stopped too, and Kubernetes
started it again.

**Question:** Did a probe cause this restart? Not directly. The container stopped on its own, and Kubernetes restarts
any container that exits. A liveness probe covers the harder case, where a program is still running but has stopped
working, such as a web server that hangs.

### Step 4: Crash loop: find the missing key

```bash
kubectl apply -f crashloop.yaml
kubectl get pods -l app=crashloop
```

After a minute the status shows `CrashLoopBackOff`. Kubernetes keeps restarting the container, and each time it
fails, it waits a little longer before the next try.

Find out why:

```bash
kubectl logs deploy/crashloop
```

The log says `DATABASE_URL is not set`. The shop's app needs to know where its database is, and nobody told it.

**Fix it:** open `crashloop.yaml` and add an `env:` section under `image: busybox:1.36`, at the same indentation:

```yaml
          env:
            - name: DATABASE_URL
              value: postgres://db.example.internal:5432/shop
```

Apply the change and check again:

```bash
kubectl apply -f crashloop.yaml
kubectl get pods -l app=crashloop
```

The pod should reach `Running` and `READY 1/1`.

### Step 5: Memory limits: a basket that is too small

```bash
kubectl apply -f memhog.yaml
kubectl get pod memhog
```

The pod runs a program that uses 150 MB of memory, but its limit is 100 MB. Kubernetes stops it for running out
of memory, and the status shows `OOMKilled` (or `Error`). Because its restart policy is `Never`, it does not restart.

Find the reason:

```bash
kubectl describe pod memhog
```

Look for `Reason: OOMKilled` in the container state section.

**Fix it:** raise the memory limit in `memhog.yaml` from `100Mi` to `250Mi`. A pod's limits cannot be changed
while it runs, so delete it and apply again:

```bash
kubectl delete pod memhog
kubectl apply -f memhog.yaml
kubectl get pod memhog
```

The status should now be `Running`.

**Question:** Why set limits at all? Without them, one greedy program can use all the memory on a computer and
slow down or crash every other pod on it.

### Step 6: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: all three scenarios fixed`.

## Clean up

```bash
kubectl delete -f healthy.yaml -f crashloop.yaml -f memhog.yaml
```

## If something goes wrong

- **`verify.sh` says `healthy` has fewer than 3 ready replicas:** a pod from step 2 may still be broken.
  Run `kubectl get pods -l app=healthy` and delete any pod that is not `1/1`.
- **`crashloop` still fails:** run `kubectl logs deploy/crashloop` again. Check that `env:` is indented under the
  container, not at the top level of the file.
- **`memhog` is still `OOMKilled`:** the pod was not recreated after you changed the limit. Delete it and apply again.
