# Lab 06: Helm

## The story

So far you have written the Kubernetes files by hand. Now imagine the shop opens a second branch. It needs the
same website, but with a different number of workers and a different nginx version.

Copying and editing the YAML files for every branch is slow and easy to get wrong. **Helm** solves this with a
**chart**: a recipe card that contains the templates, plus a list of adjustable settings called **values**.

- The templates are the recipe. They have blanks like `replicas: {{ .Values.replicaCount }}`.
- `values.yaml` holds the default settings.
- `--set` lets you change a setting for one install without editing any file.

Each install is a **release**. Helm remembers every change as a **revision**, so you can go back to an earlier one.

## What you will learn

- How a chart is laid out, and where a value ends up in the final YAML.
- How to install, upgrade, check history and roll back a release.
- Why `--reset-values` matters when you change `values.yaml`.

## Before you start

The cluster must be running, and `helm` must be installed (`helm version` should print a version). The chart,
`mychart/`, is already in this folder. Helm's `helm create` command made its starting files for you.

## Steps

### Step 1: Read the recipe card

```bash
cd labs/06-helm
ls mychart
cat mychart/values.yaml | head -20
```

You should see `Chart.yaml`, `values.yaml` and a `templates/` folder. In `values.yaml`, find:

- `replicaCount: 1`, the number of workers by default.
- `tag: "1.27"`, the nginx version by default.

Open `mychart/templates/deployment.yaml` and find `replicas:` and `image:`. They contain `{{ ... }}` blanks
that Helm fills in from `values.yaml`.

### Step 2: Install the release

```bash
helm install demo ./mychart --set image.tag=1.27
helm list
kubectl get all -l app.kubernetes.io/instance=demo
```

`helm list` shows the release `demo`. `kubectl get all` shows its pod: one, because the default
`replicaCount` is 1.

**Optional:** look at the page. Keep this command running in one terminal, and open
<http://localhost:8888> in your browser:

```bash
kubectl port-forward svc/demo-mychart 8888:80
```

Press `Ctrl+C` to stop it.

### Step 3: Change a setting without editing a file

```bash
helm upgrade demo ./mychart --set image.tag=1.27 --set replicaCount=3
kubectl get deploy -l app.kubernetes.io/instance=demo
```

The deployment now has 3 replicas. The chart did not change. Only the value you passed did.

### Step 4: Look at the history and roll back

```bash
helm history demo
helm rollback demo 1
kubectl get deploy -l app.kubernetes.io/instance=demo
```

`helm history` lists every revision. Revision 1 was the first install, with one replica. Rolling back to it
brings the replica count back to 1. A rollback creates a new revision, so the history keeps growing.

### Step 5: Preview without installing

Helm can print the final YAML without touching the cluster:

```bash
helm template demo ./mychart --set replicaCount=5 | grep replicas:
```

The output is `replicas: 5`. Helm put your value into the `replicas:` blank in `deployment.yaml`.

**Question:** Where does the `5` end up? In the template output, at the `replicas:` line of the Deployment.
Run `helm template` without the `grep` to see the whole file.

### Step 6: Change the defaults in the recipe card, then reset

Edit `mychart/values.yaml` so the defaults are:

```yaml
replicaCount: 2
image:
  tag: "1.27-alpine"
```

Now upgrade, but first look at what is overriding the file:

```bash
helm get values demo
```

You will see `image.tag: "1.27"`. That came from the `--set image.tag=1.27` you typed in step 2. Helm remembers
values you passed before, so a plain `helm upgrade` would keep `1.27` and ignore your edit.

Upgrade with `--reset-values`, which clears those old overrides and uses only `values.yaml`:

```bash
helm upgrade demo ./mychart --reset-values
kubectl get deploy -l app.kubernetes.io/instance=demo
```

The deployment now has 2 replicas of `nginx:1.27-alpine`.

**Question:** Why `--reset-values`? Values passed with `--set` override `values.yaml`, and they stick around
between upgrades unless you reset them. Without the reset, a change to the file can be silently ignored.

### Step 7: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: 2 ready replicas of <image>` with an alpine image.

## Clean up

Remove the release:

```bash
helm uninstall demo
```

## If something goes wrong

- **`verify.sh` says the release is not installed:** run `helm list`. If `demo` is missing, do step 2 again.
- **Still 1 replica after step 6:** run `helm get values demo`. If `replicaCount` or `image.tag` is listed,
  run the `--reset-values` upgrade again.
- **`Error: UPGRADE FAILED` with a message about invalid YAML:** check the indentation in `values.yaml`. YAML uses
  spaces, not tabs.
