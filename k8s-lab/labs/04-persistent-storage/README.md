# Lab 04: Persistent storage

## The story

Sam keeps a **notebook** where the time of every visit is written down. Cooks come and go. When a cook is
replaced, the new cook must still find the notebook with all the old entries.

A pod's own storage disappears with the pod, so the notebook must live somewhere else. Sam asks for a
**locker**. A **PersistentVolumeClaim** (PVC) is that request: "I need 100 MB that stays put." The cluster
provides a **PersistentVolume** (PV), the actual locker, and attaches it to the pod.

## What you will learn

- How a PVC asks for storage, and how it gets bound to a volume.
- That data stored in a pod's own filesystem disappears when the pod is deleted.
- That a volume can be tied to one computer, which matters for real clusters.

## Before you start

The cluster must be running. Lab 04 does not need labs 01 to 03.

## Steps

### Step 1: Ask for a locker and start the notebook

```bash
cd labs/04-persistent-storage
kubectl apply -f pvc.yaml -f notebook.yaml
kubectl get pvc,pv
```

`pvc.yaml` asks for 100 MB. `notebook.yaml` runs a tiny program that writes the time to
`/notebook/visitors.log` every five seconds.

The PVC may show `Pending` for a few seconds. It becomes `Bound` once the notebook pod starts and the locker is
ready. This is normal.

### Step 2: Read the notebook

```bash
kubectl exec deploy/notebook -- cat /notebook/visitors.log
```

`exec` runs a command inside the pod. You should see a list of dates and times, one per line. Run the command
again in a minute and you will see more lines.

### Step 3: Replace the cook

Delete the notebook's pod, but not the Deployment:

```bash
kubectl delete pod -l app=notebook
kubectl get pods -l app=notebook
```

Wait for the new pod to show `Running`, then read the notebook again:

```bash
kubectl exec deploy/notebook -- cat /notebook/visitors.log
```

**Question:** Are the old entries still there? They should be, because the new pod opens the same locker. The
new cook found the notebook, and kept writing from where the old one stopped.

**Challenge:** Change `notebook.yaml` to use `emptyDir` instead of the PVC. This is temporary storage that is
removed with the pod, like writing on the back of your hand. Apply the change, delete the pod, and read the
file again. The old entries are gone. Change the file back to the PVC afterwards.

### Step 4: Find out where the locker is

```bash
kubectl get pv -o yaml | grep -A6 nodeAffinity
```

Look for `kubernetes.io/hostname`. It names the one worker computer the locker lives on.

**Question:** What does this mean for scheduling? The notebook pod must run on that computer, because the
locker only exists there.

**Question:** Why does this not work well for real multi-node clusters without network storage? If that
computer fails, the notebook is stuck on it. Real clusters use storage that any worker can reach, such as cloud
disks or network file systems, so the data survives a failed computer.

### Step 5: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: locker bound and <n> notebook lines present`.

## Clean up

When you are finished, remove the notebook and its locker:

```bash
kubectl delete -f notebook.yaml -f pvc.yaml
```

Deleting the PVC empties the locker for good. This is what "persistent" means: the data lasts until you delete
the claim.

## If something goes wrong

- **PVC stays `Pending`:** run `kubectl describe pvc notebook-locker` and read the Events section. The notebook
  pod must exist for the locker to be created.
- **`verify.sh` says no lines:** the notebook may have just started. Wait 10 seconds and run the check again.
