# Lab 06: Helm

## The story

So far you have written the Kubernetes files by hand. Now Sam wants a second stall at another fair: the same
stall, but bigger, with four cooks instead of two.

Copying and editing the YAML files for every stall is slow and easy to get wrong. **Helm** solves this with a
**chart**: one recipe card for a whole stall, with small settings tags hanging from it called **values**. This
card is not the burger recipe from the Docker lab. That card made one box. This one describes a whole stall:
which image its cooks use, and how many cooks it has.

- The templates are the card. They have blanks like `replicas: {{ .Values.replicaCount }}`.
- `values.yaml` holds the default settings.
- `--set` changes a setting for one install without editing any file.

Each install is a **release**. One card can make many releases, each with its own settings. Helm remembers
every change to a release as a **revision**, so you can go back to an earlier one.

## What you will learn

- How a chart is laid out, and where a value ends up in the final YAML.
- How one chart makes several releases with different settings.
- How to install, upgrade, check history and roll back a release.
- Why `--reset-values` matters when you change `values.yaml`.

## Before you start

The cluster must be running, and `helm` must be installed (`helm version` should print a version). The chart,
`stall/`, is already in this folder. Helm's `helm create` command made its starting files.

## Steps

### Step 1: Read the recipe card

```bash
cd labs/06-helm
ls stall
head -20 stall/values.yaml
```

You should see `Chart.yaml`, `values.yaml` and a `templates/` folder. In `values.yaml`, find:

- `replicaCount: 1`, the number of cooks by default.
- `tag: "1.27"`, the nginx version by default.

Open `stall/templates/deployment.yaml` and find `replicas:` and `image:`. They contain `{{ ... }}` blanks that
Helm fills in from the values.

### Step 2: Open a small stall

```bash
helm install small-stall ./stall --set image.tag=1.27 --set replicaCount=2
helm list
kubectl get deploy small-stall
```

`helm list` shows the release `small-stall`. The deployment shows `READY 2/2`: two cooks, because you set
`replicaCount=2`.

**Optional:** look at the page. Keep this command running in one terminal, and open
<http://localhost:8888> in your browser:

```bash
kubectl port-forward svc/small-stall 8888:80
```

Press `Ctrl+C` to stop it.

### Step 3: Open a big stall from the same card

```bash
helm install big-stall ./stall --set image.tag=1.27 --set replicaCount=4
kubectl get deploy small-stall big-stall
```

`small-stall` has two cooks and `big-stall` has four.

**Question:** Did the card change? No. You installed the same chart twice, with a different setting each time.

### Step 4: Change a setting, look at the history and roll back

```bash
helm upgrade small-stall ./stall --set image.tag=1.27 --set replicaCount=3
kubectl get deploy small-stall
```

The small stall now has three cooks. Look at its history, then go back to the first revision:

```bash
helm history small-stall
helm rollback small-stall 1
kubectl get deploy small-stall
```

`helm history` lists every revision. Revision 1 was the first install, with two cooks. Rolling back brings the
count back to 2. A rollback creates a new revision, so the history keeps growing.

### Step 5: Preview without installing

Helm can print the final YAML without touching the cluster:

```bash
helm template small-stall ./stall --set replicaCount=5 | grep replicas:
```

The output is `replicas: 5`. Helm put your value into the `replicas:` blank in `deployment.yaml`.

**Question:** Where does the `5` end up? In the template output, at the `replicas:` line of the Deployment.
Run `helm template` without the `grep` to see the whole file.

### Step 6: Change the defaults on the card, then reset

Edit `stall/values.yaml` so the defaults are:

```yaml
replicaCount: 2
image:
  tag: "1.27-alpine"
```

Now look at what is overriding the file for the small stall:

```bash
helm get values small-stall
```

You will see `image.tag: "1.27"` and `replicaCount: 2`. They came from the `--set` options you typed in step 2.
Helm remembers values you passed before, so a plain `helm upgrade` would keep `1.27` and ignore your edit.

Upgrade with `--reset-values`, which clears those old overrides and uses only `values.yaml`:

```bash
helm upgrade small-stall ./stall --reset-values
kubectl get deploy small-stall -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```

The small stall now has two cooks on `nginx:1.27-alpine`.

**Question:** Did the big stall change too? No. A release changes only when you upgrade it. `big-stall` keeps
its four cooks on `nginx:1.27`.

**Question:** Why `--reset-values`? Values passed with `--set` override `values.yaml`, and they stay between
upgrades unless you reset them. Without the reset, a change to the file can be silently ignored.

### Step 7: Check your work

```bash
bash verify.sh
```

Expected output: `PASS: one recipe card, two stalls: small-stall has 2 cooks on nginx:1.27-alpine, big-stall has 4`.

## Clean up

Close both stalls:

```bash
helm uninstall small-stall big-stall
```

## If something goes wrong

- **`verify.sh` says a release is not installed:** run `helm list`. If one is missing, do step 2 or step 3 again.
- **Still on `nginx:1.27` after step 6:** run `helm get values small-stall`. If `image.tag` is listed, run the
  `--reset-values` upgrade again.
- **`Error: UPGRADE FAILED` with a message about invalid YAML:** check the indentation in `values.yaml`. YAML uses
  spaces, not tabs.
