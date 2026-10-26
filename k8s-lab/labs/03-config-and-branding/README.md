# Lab 03: ConfigMaps, Secrets and the stall's sign

## The story

Sam's stalls need a sign: the stall's name, a welcome line and the burger logo. The sign is not part of the
nginx recipe card, and Sam does not want to pack new boxes every time the sign changes.

So Sam uses the back room. Kubernetes gives it two places to keep things outside the recipe:

- A **ConfigMap** is the **notice board**. Sam pins the sign's page and the logo to it, and every cook reads
  them from there.
- A **Secret** is the **safe**, for things not everyone should see, such as the secret sauce recipe. Only the
  cooks who are allowed to open it can read what is inside.

## What you will learn

- How to create a ConfigMap from files and mount it into a pod.
- How a changed ConfigMap reaches running pods, and when a restart is needed.
- How to create a Secret and read it back, and why base64 is not encryption.

## Before you start

Make sure the cluster is running (`kubectl get nodes` shows three `Ready` nodes). The logo is already in
`labs/03-config-and-branding/assets/burger.png`.

## Steps

### Step 1: Pin the page and the logo to the notice board

```bash
cd labs/03-config-and-branding
kubectl create configmap sign-html --from-file=index.html
kubectl create configmap sign-logo --from-file=assets/burger.png
```

Look inside the ConfigMap:

```bash
kubectl get configmap sign-html -o yaml
```

Your HTML is in the `data:` section. A ConfigMap holds only text and small files, so it is a simple way to pass
files to pods without packing a new image.

> If you see `AlreadyExists`, you created these in an earlier attempt. Keep them, or delete them with
> `kubectl delete configmap sign-html sign-logo` and create them again.

### Step 2: Put up the sign

```bash
kubectl apply -f sign.yaml
```

This creates two pods and a Service that uses port 30081. Open <http://localhost:8081>. You should see the
**Sam's Burger Stall** page with the burger logo. If the logo is missing, the page still works without it.

**Look at `sign.yaml`:** the `volumes:` section joins both ConfigMaps into one folder, and
`volumeMounts:` places that folder at `/usr/share/nginx/html`, where nginx serves files from.

### Step 3: Change the sign

Open `index.html` and change the heading text. Then update the ConfigMap:

```bash
kubectl create configmap sign-html --from-file=index.html --dry-run=client -o yaml | kubectl apply -f -
```

Wait about a minute, then refresh <http://localhost:8081>.

**Question:** Did the page change without restarting any pods? It should, once the new content reaches the
pods. Files from a ConfigMap are updated in place, and nginx reads the new file.

Now compare with a restart:

```bash
kubectl rollout restart deploy/stall-sign
kubectl rollout status deploy/stall-sign
```

The pods are replaced with new ones. The page is still correct, but restarting was not the only way to get it.

**Question:** Why the difference? Restarts are needed for changes that a running program reads only at start,
such as environment variables. Files mounted from a ConfigMap update by themselves.

### Step 4: Lock the secret sauce in the safe

Create a Secret and read it back:

```bash
kubectl create secret generic secret-sauce --from-literal=recipe=smoky-garlic
kubectl get secret secret-sauce -o jsonpath='{.data.recipe}' | base64 -d; echo
```

The second command prints `smoky-garlic`.

**Question:** Is base64 encryption? No. Base64 only changes how the text looks. Anyone who can read the Secret
can decode it in one step, as you just did.

**Question:** Who can open the safe in a real cluster, and how would you restrict it? Access is controlled with
Kubernetes permissions (RBAC). You give each user or program only the access it needs. You also keep secret
values out of files that go into Git.

### Step 5: Check your work

```bash
bash verify.sh
```

Expected output:

```text
PASS: stall sign reachable on :8081
PASS: secret-sauce exists
```

## Clean up

Leave the sign up. Lab 05 and later do not depend on it.

## If something goes wrong

- **Page does not open on 8081:** run `kubectl get svc stall-sign`. The `PORT(S)` column must show `30081`.
- **`kubectl apply -f sign.yaml` says `configmap "sign-html" not found`:** pods will wait until the
  ConfigMaps exist. Do step 1 first, then run `kubectl get pods`.
- **The logo is missing:** check that `assets/burger.png` exists. The page still works without it.
