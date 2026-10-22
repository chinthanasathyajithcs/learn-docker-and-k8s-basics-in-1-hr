# Lab 04: Persistent storage

## The story

The shop keeps a **notebook** where every visitor is logged with the time they arrived. Workers come and go.
When a worker is replaced, the new worker must still find the notebook with all the old entries.

A pod's own storage disappears with the pod, so the notebook must live somewhere else. You ask for a **locker**.
A **PersistentVolumeClaim** (PVC) is that request: "I need 100 MB that stays put." The cluster provides a
**PersistentVolume** (PV), the actual locker, and attaches it to your pod.

## What you will learn

- How a PVC asks for storage, and how it gets bound to a volume.
- That data stored in a pod's own filesystem disappears when the pod is deleted.
- That a volume can be tied to one computer, which matters for real clusters.

## Before you start

The cluster must be running. Lab 04 does not need labs 01 to 03.

## Steps

### Step 1: Ask for a locker and start the logger

```bash
cd labs/04-persistent-storage
kubectl apply -f pvc.yaml -f logger.yaml
kubectl get pvc,pv
```

`pvc.yaml` asks for 100 MB. `logger.yaml` runs a tiny program that writes the time to `/data/log.txt` every
five seconds.

The PVC may show `Pending` for a few seconds. It becomes `Bound` once the logger pod starts and the locker is
ready. This is normal.

### Step 2: Read the notebook

```bash
kubectl exec deploy/logger -- cat /data/log.txt
```

`exec` runs a command inside the pod. You should see a list of dates and times, one per line. Run the command
again in a minute and you will see more lines.

### Step 3: Replace the worker

Delete the logger's pod, but not the Deployment:

```bash
kubectl delete pod -l app=logger
kubectl get pods -l app=logger
```

Wait for the new pod to show `Running`, then read the notebook again:

```bash
kubectl exec deploy/logger -- cat /data/log.txt
```

**Question:** Are the old entries still there? They should be, because the new pod mounts the same locker.
The new worker found the notebook, and it kept writing from where the old one stopped.

**Challenge:** Change `logger.yaml` to use `emptyDir` instead of the PVC. This is temporary storage that is
removed with the pod. Apply the change, delete the pod, and read the file again. The old entries are gone.
Change the file back to the PVC afterwards.

### Step 4: Find out where the locker is

```bash
kubectl get pv -o yaml | grep -A6 nodeAffinity
```

Look for `kubernetes.io/hostname`. It names the one worker computer the locker lives on.

**Question:** What does this mean for scheduling? The logger pod must run on that computer, because the locker
only exists there.

**Question:** Why does this not work well for real multi-node clusters without network storage? If that
computer fails, the data is stuck on it. Real clusters use storage that any worker can reach, such as cloud
disks or network file systems, so the data survives a failed computer.

### Step 5: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: PVC bound and <n> log lines present`.

## Clean up

When you are finished, remove the logger and its locker:

```bash
kubectl delete -f logger.yaml -f pvc.yaml
```

Deleting the PVC deletes the notebook. This is what "persistent" means: the data lasts until you delete the claim.

## If something goes wrong

- **PVC stays `Pending`:** run `kubectl describe pvc logger-data` and read the Events section. The logger pod
  must exist for the locker to be created.
- **`verify.sh` says no data:** the logger may have just started. Wait 10 seconds and run the check again.
