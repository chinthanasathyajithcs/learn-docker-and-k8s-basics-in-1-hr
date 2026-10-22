# Lab 03: ConfigMaps, Secrets and a branded site

## The story

The shop wants its website to carry two logos and a welcome message. The logos and the page are not part of
the nginx recipe, so you do not want to build a new image every time the sign changes.

Instead you use two kinds of **notice boards** Kubernetes provides:

- A **ConfigMap** is a notice board for ordinary settings and files. You can pin the shop's HTML page and logo
  files to it, and the workers read them from there.
- A **Secret** is a locked safe for sensitive values, such as passwords. Only the workers who are allowed
  to open it can read its contents.

## What you will learn

- How to create a ConfigMap from files and mount it into a pod.
- How a changed ConfigMap reaches running pods, and when a restart is needed.
- How to create a Secret and read it back, and why base64 is not encryption.

## Before you start

Make sure the cluster is running (`kubectl get nodes` shows three `Ready` nodes). The logo files are already in
`labs/03-config-and-branding/assets/`.

## Steps

### Step 1: Pin the page and logos to the notice boards

```bash
cd labs/03-config-and-branding
kubectl create configmap site-html --from-file=index.html
kubectl create configmap site-logos --from-file=assets/ifs.png --from-file=assets/nsbm.png
```

Look inside the ConfigMap:

```bash
kubectl get configmap site-html -o yaml
```

Your HTML is in the `data:` section. A ConfigMap is only text and small files, so it is a simple way to pass
files to pods without a new image.

> If you see `AlreadyExists`, you created these in an earlier attempt. Keep them, or delete them with
> `kubectl delete configmap site-html site-logos` and create them again.

### Step 2: Open the shop sign

```bash
kubectl apply -f site.yaml
```

This creates two pods and a Service that uses port 30081. Open <http://localhost:8081>. You should see the
**IFS x NSBM** page with both logos. If a logo is missing, the page shows its name as text instead, and the
page still works.

**Look at `site.yaml`:** the `volumes:` section joins both ConfigMaps into one folder, and
`volumeMounts:` places that folder at `/usr/share/nginx/html`, where nginx serves files from.

### Step 3: Change the sign

Open `index.html` and change the heading text. Then update the ConfigMap:

```bash
kubectl create configmap site-html --from-file=index.html --dry-run=client -o yaml | kubectl apply -f -
```

Wait about a minute, then refresh <http://localhost:8081>.

**Question:** Did the page change without restarting any pods? It should, once the new content reaches the
pods. Files from a ConfigMap are updated in place, and nginx reads the new file.

Now compare with a restart:

```bash
kubectl rollout restart deploy/site
kubectl rollout status deploy/site
```

The pods are replaced with new ones. The page is still correct, but restarting was not the only way to get it.

**Question:** Why the difference? Restarts are needed for changes that a running process reads only at start,
such as environment variables. Files mounted from a ConfigMap update by themselves.

### Step 4: Lock something in the safe

Create a Secret and read it back:

```bash
kubectl create secret generic site-secret --from-literal=team=gamma
kubectl get secret site-secret -o jsonpath='{.data.team}' | base64 -d; echo
```

The second command prints `gamma`.

**Question:** Is base64 encryption? No. Base64 only changes how the text looks. Anyone who can read the Secret
can decode it in one step, as you just did.

**Question:** Who can read this in a real cluster, and how would you restrict it? Access is controlled with
Kubernetes permissions (RBAC). You give each user or program only the access it needs. You also keep secret
values out of files that go into Git.

### Step 5: Check your work

```bash
bash verify.sh
```

Expected output:

```text
PASS: site reachable on :8081
PASS: site-secret exists
```

## Clean up

Leave the site running. Lab 05 and later do not depend on it.

## If something goes wrong

- **Page does not open on 8081:** run `kubectl get svc site`. The `PORT(S)` column must show `30081`.
- **`kubectl apply -f site.yaml` says `configmap "site-html" not found`:** pods will wait until the
  ConfigMaps exist. Do step 1 first, then run `kubectl get pods`.
- **Logo shows as text:** the logo files may be missing from `assets/`. The page still works without them.
