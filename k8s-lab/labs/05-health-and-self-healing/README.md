# Lab 05: Probes, limits and self-healing

## The story

Every morning, before the fair gets busy, Sam walks past the three stalls with the clipboard. Kubernetes does
the same check all day, using two different questions:

- **Readiness: "Are you ready for customers?"** A cook who answers "no" gets a rope across their counter, and
  the front desk sends nobody there. The cook is not sent home, and may be ready soon.
- **Liveness: "Are you still alive?"** A cook who answers "no" is replaced with a fresh start.

Some cooks are also given a **memory limit**: the most they may carry at once. A cook who tries to carry a tower
of boxes taller than the limit is stopped.

Finally, some cooks are stuck in ways you must fix yourself: a missing address that stops them starting, and
a limit that is too small for the job.

## What you will learn

- The difference between readiness and liveness probes, and what each one does.
- How Kubernetes restarts a crashing container, and how to find out why it crashed.
- How memory limits work, and how to read the reason a pod was stopped.

## Before you start

The cluster must be running. Lab 05 does not depend on earlier labs.

## Steps

### Step 1: Open three stalls for the morning

```bash
cd labs/05-health-and-self-healing
kubectl apply -f morning-stall.yaml
kubectl get pods -l app=morning-stall
```

Wait until all three pods show `READY 1/1`. `morning-stall.yaml` also contains a Service named
`morning-stall`, which is the front desk for these cooks.

### Step 2: Readiness: put a rope across one counter

Pick one pod and delete its web page, so nginx has nothing to serve:

```bash
POD=$(kubectl get pod -l app=morning-stall -o name | head -1)
kubectl exec $POD -- rm /usr/share/nginx/html/index.html
kubectl get pods -l app=morning-stall -w
```

Press `Ctrl+C` after about 15 seconds. The broken pod is still `Running`, but `READY` shows `0/1`.

Check the front desk's list:

```bash
kubectl get endpoints morning-stall
```

The broken pod's address is gone. Customers now go only to the two ready cooks.

**Question:** Why was the broken pod not restarted? The readiness probe only decides whether a pod receives
customers. A pod that is not ready is left alone, in case it recovers. Restarting it would not help, because
the probe checks the page, and a restart would not put the file back.

**Fix it:** delete the broken pod, and the Deployment will bring in a fresh cook:

```bash
kubectl delete pod $POD
kubectl get pods -l app=morning-stall
```

Wait until all three pods show `READY 1/1`.

### Step 3: Liveness: a cook who stops is restarted

Stop nginx inside one pod:

```bash
POD=$(kubectl get pod -l app=morning-stall -o name | head -1)
kubectl exec $POD -- nginx -s stop
kubectl get pods -l app=morning-stall
```

Look at the `RESTARTS` column. It goes up to `1`. When nginx stopped, the container stopped too, and Kubernetes
started it again.

**Question:** Did a probe cause this restart? Not directly. The container stopped on its own, and Kubernetes
restarts any container that exits. A liveness probe covers the harder case, where a program is still running
but has stopped working, such as a web server that hangs.

### Step 4: Crash loop: find the missing address

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

The log says `DATABASE_URL is not set`. This cook needs to know where the filing cabinet is, and nobody told
them.

**Fix it:** open `crashloop.yaml` and add an `env:` section under `image: busybox:1.36`, at the same
indentation:

```yaml
          env:
            - name: DATABASE_URL
              value: postgres://cabinet.example.internal:5432/stall
```

Apply the change and check again:

```bash
kubectl apply -f crashloop.yaml
kubectl get pods -l app=crashloop
```

The pod should reach `Running` and `READY 1/1`.

### Step 5: Memory limits: a tower of boxes too tall

```bash
kubectl apply -f memhog.yaml
kubectl get pod memhog
```

The pod runs a program that uses 150 MB of memory, but its limit is 100 MB. Kubernetes stops it for running out
of memory, and the status shows `OOMKilled` (or `Error`). Because its restart policy is `Never`, it does not
restart.

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
kubectl delete -f morning-stall.yaml -f crashloop.yaml -f memhog.yaml
```

## If something goes wrong

- **`verify.sh` says `morning-stall` has fewer than 3 ready cooks:** a pod from step 2 may still be broken.
  Run `kubectl get pods -l app=morning-stall` and delete any pod that is not `1/1`.
- **`crashloop` still fails:** run `kubectl logs deploy/crashloop` again. Check that `env:` is indented under the
  container, not at the top level of the file.
- **`memhog` is still `OOMKilled`:** the pod was not recreated after you changed the limit. Delete it and apply again.
