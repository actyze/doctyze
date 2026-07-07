---
doctyze:
  artifact: runbook
  generated_by: write-runbook
  affects: [k8s/db.yml, k8s/petclinic.yml, .github/workflows/deploy-and-test-cluster.yml, .github/workflows/maven-build.yml, .github/workflows/gradle-build.yml]
  last_verified: 2026-07-06
---
# Runbook — CI/CD and Kubernetes deployment

## Summary

This repo carries three GitHub Actions workflows and two Kubernetes manifests. The workflows cover build
verification (Maven and Gradle) and a smoke-test of the k8s manifests on an ephemeral Kind cluster. The
manifests (`k8s/db.yml`, `k8s/petclinic.yml`) deploy PetClinic against a Postgres database using a
service-binding secret. **What is documented here is exactly what those files declare** — there is no Helm
chart, no image-publishing step, and no cloud/production target in the repo, and this runbook says so where
that is the case.

## CI pipelines

### `Java CI with Maven` — `.github/workflows/maven-build.yml`

- **Job:** `build`, on `ubuntu-latest`, Java matrix `[ '17' ]` (`adopt` distribution, Maven cache).
- **Trigger:** `push` and `pull_request` on `main`.
- **Step:** `Build with Maven Wrapper` → `./mvnw -B verify`. As covered in
  `docs/runbooks/build-and-run.md`, `verify` also runs format/checkstyle validation, JaCoCo, and SBOM
  generation.

### `Java CI with Gradle` — `.github/workflows/gradle-build.yml`

- **Job:** `build`, `ubuntu-latest`, Java matrix `[ '17' ]`.
- **Trigger:** `push` / `pull_request` on `main`.
- **Steps:** `gradle/actions/setup-gradle@v4`, then `Build with Gradle` → `./gradlew build`.

> Neither build workflow publishes an artifact or a container image — they verify the build only.

### `Deploy and Test Cluster` — `.github/workflows/deploy-and-test-cluster.yml`

- **Job:** `deploy-and-test-cluster`, `ubuntu-latest`.
- **Trigger:** `push` / `pull_request` on `main`, **path-filtered to `k8s/**`** — it only runs when the
  Kubernetes manifests change.
- **Steps:**
  1. Checkout (`actions/checkout@v2`).
  2. `Create k8s Kind Cluster` (`helm/kind-action@v1`).
  3. `Deploy application` → `kubectl apply -f k8s/` (applies **both** manifests).
  4. `Wait for Pods to be ready`:
     ```bash
     kubectl wait --for=condition=ready pod -l app=demo-db --timeout=180s
     kubectl wait --for=condition=ready pod -l app=petclinic --timeout=180s
     ```

This is a manifest smoke-test: it proves the pods reach `Ready` on a throwaway cluster. It does not run
application-level assertions.

## Kubernetes manifests

Apply both together (as CI does):

```bash
kubectl apply -f k8s/
```

### Database — `k8s/db.yml`

Declares three objects, all named `demo-db`:

- **Secret `demo-db`** of type `servicebinding.io/postgresql` with `stringData`: `type`/`provider`
  `postgresql`, `host: demo-db`, `port: "5432"`, `database: petclinic`, `username: user`, `password: pass`.
  These are **demo credentials committed in-repo** — fine for Kind, not for production.
- **Service `demo-db`** exposing `port: 5432` (selector `app: demo-db`).
- **Deployment `demo-db`** running `postgres:18.4`, injecting `POSTGRES_USER`/`POSTGRES_PASSWORD`/
  `POSTGRES_DB` from the secret, and using **`tcpSocket`** liveness, readiness, and startup probes on the
  `postgresql` (5432) port.

### Application — `k8s/petclinic.yml`

- **Service `petclinic`** of type **`NodePort`**, mapping `port: 80` → `targetPort: 8080` (selector
  `app: petclinic`).
- **Deployment `petclinic`**, `replicas: 1`, container `workload` from image **`dsyer/petclinic`** (a
  prebuilt public image — this repo does not build or push it).
  - **Env:**
    - `SPRING_PROFILES_ACTIVE=postgres` — so the app runs on the Postgres profile
      (`application-postgres.properties`).
    - `SERVICE_BINDING_ROOT=/bindings` — where the app reads bound credentials.
    - `SPRING_APPLICATION_JSON` sets `management.endpoint.health.probes.add-additional-paths: true`, which
      is what enables the `/livez` and `/readyz` health paths (see below and
      `docs/observability/observability.md`).
  - **Port:** `http` = `containerPort: 8080`.
  - **Probes:** HTTP `livenessProbe` → `/livez`, `readinessProbe` → `/readyz` (both on the `http` port).
  - **Volume:** projects the `demo-db` secret at `/bindings/secret` (read-only), consumed via the
    `SERVICE_BINDING_ROOT` convention so the app discovers the Postgres connection without hard-coded
    datasource properties.

### Access the app after deploy

Because the Service is `NodePort` (not a LoadBalancer or Ingress — neither is defined in-repo), reach it by
port-forwarding:

```bash
kubectl port-forward service/petclinic 8080:80
# then open http://localhost:8080/
```

## What is NOT in this repo (do not assume)

- No `Dockerfile` and no image-build/push step in CI — the k8s deploy relies on the external
  `dsyer/petclinic` image (build your own image per `docs/runbooks/build-and-run.md` if you need one).
- No Helm chart, Kustomize overlays, or environment-specific (staging/prod) manifests — only the two flat
  files under `k8s/`.
- No Ingress, TLS, HPA, resource requests/limits, or namespace declarations in the manifests.
- No documented rollback automation; use standard Kubernetes rollout controls
  (`kubectl rollout undo deployment/petclinic`).
