# HELEP Orchestration Guidelines

This file is your private learning guide for completing the HELEP 24-hour orchestration exercise on Windows. It is intentionally ignored by Git because it is a working notebook, not a submission artifact.

The goal is not to blindly run commands. For each stage, this guide explains:

- what you are doing,
- why it matters for the project requirements,
- how to do it,
- which commands to run,
- what output to expect,
- what evidence to capture,
- what to write in your Google Doc deliverables.

The project requires Jenkins for CI/CD. Do not use GitHub Actions for this project.

---

## 0. Project Understanding

### What HELEP Is

HELEP is an emergency response platform implemented as five Python FastAPI microservices:

- `user-service`: handles identity, login, JWTs, credibility, and emergency contacts.
- `sos-service`: receives SOS triggers and cancellations.
- `dispatch-service`: assigns responders and handles danger-zone matching.
- `notification-service`: simulates SMS/push notification delivery.
- `analytics-service`: consumes events and exposes police/statistics endpoints.

The system uses:

- Apache Kafka for asynchronous event communication.
- SQLite per service for persistence.
- Docker for containerization.
- Kubernetes for orchestration.
- Helm for packaging Kubernetes resources.
- Strimzi for Kafka on Kubernetes.
- Prometheus and Grafana for monitoring.
- Jenkins for CI/CD.

### What Is Already Provided

The starter code already includes:

- FastAPI services.
- `/healthz`, `/readyz`, and `/metrics` endpoints.
- Kafka producers and consumers.
- SQLite repository modules.
- A choreographed saga skeleton.
- Strategy pattern for dispatch matching.
- Docker Compose dev stack.
- Design and patterns document templates.

### What You Must Add

The main work is:

- Complete the circuit breaker implementation.
- Add a third dispatch matching strategy.
- Add Dockerfiles for all services.
- Build Kubernetes and Helm deployment artifacts.
- Deploy Kafka using Strimzi.
- Add Prometheus/Grafana monitoring.
- Add Jenkins CI/CD.
- Produce design and patterns PDFs.
- Record a demo video.
- Collect evidence.

---

## 1. Google Doc Documentation Structure

You will document the project in a Google Doc with one tab or section per deliverable.

Use this structure:

1. Project Overview
2. Environment Setup
3. Baseline Docker Compose Smoke Test
4. Code-Level Pattern Work
5. Containerization
6. Kubernetes and Helm Deployment
7. Strimzi Kafka Deployment
8. Monitoring with Prometheus and Grafana
9. Jenkins CI/CD
10. Design Process Document Notes
11. Patterns-in-Code Document Notes
12. Demo Evidence and Final Submission Checklist

Each section should follow this mini-template:

```markdown
## <Section Title>

### Purpose
Explain what this step proves or contributes to the project.

### Requirement Addressed
Mention the project requirement, SRS item, or architectural driver.

### Work Performed
Describe the task in your own words.

### Commands Used
Paste commands you ran.

### Results Observed
Paste short outputs or summarize screenshots.

### Evidence Captured
List screenshots, logs, command outputs, or video clips.

### Defense/Justification
Explain why this implementation choice is correct.
```

Do not dump huge command logs. Capture the key lines that prove success.

---

## 2. Tool Installation

### Purpose

This step prepares your Windows machine for containerization, orchestration, documentation, and CI/CD.

You already have:

- Docker Desktop
- Docker Compose
- Kubernetes CLI through Chocolatey
- Minikube
- Git
- Chocolatey
- Python launcher as `py`

You still need:

- Helm
- Pandoc
- MiKTeX or another LaTeX engine for PDF export
- Jenkins
- Java runtime for Jenkins
- GitHub CLI is optional, but not required because CI/CD must be Jenkins.

### Install Helm

What this does:

Helm is the package manager for Kubernetes. We use it to deploy HELEP as an umbrella chart and to install external stacks like Strimzi and Prometheus.

Command:

```powershell
choco install kubernetes-helm -y
```

Expected output:

```text
The install of kubernetes-helm was successful.
```

Verify:

```powershell
helm version
```

Expected output:

```text
version.BuildInfo{Version:"v..."}
```

Document:

- Screenshot or pasted output of `helm version`.
- One sentence: "Helm is required to package and deploy the Kubernetes resources reproducibly."

### Install Pandoc and PDF Support

What this does:

Pandoc converts the filled Markdown templates into PDF files.

Commands:

```powershell
choco install pandoc -y
choco install miktex -y
```

Verify:

```powershell
pandoc --version
```

Expected output:

```text
pandoc.exe ...
```

Document:

- Output of `pandoc --version`.
- Explain that Markdown keeps documentation traceable in the repo before export to PDF.

### Install Jenkins and Java

What this does:

Jenkins is the required CI/CD system. It will run the build and validation pipeline for the project.

Recommended Windows setup:

```powershell
choco install temurin17 -y
choco install jenkins -y
```

Restart your terminal after installation.

Verify Java:

```powershell
java -version
```

Expected output:

```text
openjdk version "17..."
```

Check Jenkins service:

```powershell
Get-Service jenkins
```

Expected output:

```text
Status   Name      DisplayName
Running  jenkins   Jenkins
```

Open Jenkins:

```text
http://localhost:8080
```

Get the initial admin password:

```powershell
Get-Content "C:\Program Files\Jenkins\secrets\initialAdminPassword"
```

Expected output:

```text
<long generated password>
```

Document:

- Jenkins dashboard screenshot.
- Java version.
- Jenkins service status.
- Explain that Jenkins is used instead of GitHub Actions because the project requirements mandate Jenkins.

---

## 3. Kubernetes Cluster Setup with Minikube

### Purpose

This step creates the local Kubernetes cluster where the application, Kafka, and monitoring stack will run.

### Why Minikube

Minikube is already installed and works well for a local Windows learning setup. It creates a single-node Kubernetes cluster using Docker.

### Start Minikube

Command:

```powershell
minikube start --driver=docker --cpus=4 --memory=8192
```

What the command does:

- `minikube start` creates or starts the local cluster.
- `--driver=docker` tells Minikube to run Kubernetes inside Docker.
- `--cpus=4` gives the cluster enough CPU for Kafka and services.
- `--memory=8192` gives the cluster 8 GB RAM.

Expected output:

```text
Done! kubectl is now configured to use "minikube" cluster
```

Verify:

```powershell
kubectl config current-context
kubectl get nodes
```

Expected output:

```text
minikube
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   ...   v...
```

Enable useful addons:

```powershell
minikube addons enable ingress
minikube addons enable metrics-server
```

What these do:

- `ingress` allows HTTP routing into the cluster.
- `metrics-server` provides CPU/memory metrics needed by HPA.

Document:

- `kubectl get nodes` output.
- Addon enable output.
- Explain that Kubernetes is the orchestration layer required by the exercise.

---

## 4. Baseline Docker Compose Smoke Test

### Purpose

Before changing Kubernetes files, prove that the application logic works locally in the provided dev stack.

### Why

If the saga fails in Docker Compose, Kubernetes will not fix it. This baseline separates application behavior from orchestration packaging.

### Start the Dev Stack

Command:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

What the command does:

- Builds temporary service images using inline Dockerfiles in the compose file.
- Starts Kafka and all five services.
- Mounts named Docker volumes for service SQLite data.

Expected output:

```text
kafka-1                Healthy
user-service-1         Started
sos-service-1          Started
dispatch-service-1     Started
notification-service-1 Started
analytics-service-1    Started
```

### Create a User

Open a second terminal.

Command:

```powershell
curl.exe -X POST localhost:8001/signup -H "content-type: application/json" -d "{\"phone\":\"+237600000001\",\"password\":\"hunter22\",\"role\":\"citizen\"}"
```

Or alternatively

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/signup" -Method Post -ContentType "application/json" -Body '{"phone":"+237600000001","password":"hunter22","role":"citizen"}'
```

What the command does:

- Sends a signup request to `user-service`.
- Creates a citizen user.
- Returns a JWT token used to authenticate SOS calls.

Expected output:

```json
{"id":"...","token":"eyJ..."}
```

Copy the token.

### Trigger an SOS

Command:

```powershell
curl.exe -X POST localhost:8002/sos -H "authorization: Bearer <TOKEN>" -H "content-type: application/json" -d "{\"lat\":4.0500,\"lon\":9.7700,\"mode\":\"online\"}"
```

Or alternatively

```powershell
Invoke-RestMethod -Uri "http://localhost:8002/sos" -Method Post -Headers @{ Authorization = "Bearer <TOKEN>" } -ContentType "application/json" -Body '{"lat":4.0500,"lon":9.7700,"mode":"online"}'
```

What the command does:

- Sends an SOS event to `sos-service`.
- `sos-service` stores the incident.
- `sos-service` publishes `sos.triggered` to Kafka.
- `dispatch-service` consumes the event and assigns a responder.
- `notification-service` sends simulated notification logs.
- `analytics-service` updates statistics.

Expected output:

```json
{"incident_id":"...","status":"ACTIVE"}
```

### Check Analytics

Commands:

```powershell
curl.exe localhost:8005/stats/events
curl.exe localhost:8005/stats/zones
```

Expected output:

```json
[{"stream":"sos.triggered","n":1}, ...]
```

### Check Notification Logs

Command:

```powershell
docker compose -f docker-compose.dev.yml logs notification-service
```

Expected output:

```text
notification.delivered
```

Document:

- Signup response.
- SOS response.
- Analytics output.
- Notification log line.
- Explain that this proves the event-driven saga works before Kubernetes packaging.

---

## 5. Code-Level Required Work

### Purpose

Complete the code requirements mentioned in the templates:

- Circuit breaker state machine.
- Third dispatch strategy.

### Circuit Breaker

What you are doing:

You will complete `class CircuitBreaker` in every service's `app/events.py`.

Why:

The template explicitly requires the circuit breaker stub to be completed and cited in the patterns document.

Behavior to implement:

- CLOSED: normal state, Kafka publishing allowed.
- OPEN: publishing blocked after repeated failures.
- HALF_OPEN: after a timeout, allow one test publish.
- On success: reset failures and close the breaker.
- On failure: reopen the breaker.

Files:

```text
services/user-service/app/events.py
services/sos-service/app/events.py
services/dispatch-service/app/events.py
services/notification-service/app/events.py
services/analytics-service/app/events.py
```

Evidence commands:

```powershell
findstr /n "class CircuitBreaker" services\user-service\app\events.py
findstr /n "def allow" services\user-service\app\events.py
findstr /n "record_failure" services\user-service\app\events.py
```

Document:

- Cite file and line numbers in the patterns document.
- Explain state transitions.
- Explain the trade-off: circuit breakers improve resilience but can temporarily reject publishes while Kafka recovers.

### Third Dispatch Strategy

What you are doing:

Add a third matcher to `dispatch-service/app/matching.py`.

Recommended strategy:

```text
round_robin
```

Why:

The patterns template requires adding a third strategy and citing it.

Files:

```text
services/dispatch-service/app/matching.py
```

Expected behavior:

- `MATCHER=nearest` uses nearest responder.
- `MATCHER=credibility` uses credibility-weighted matching.
- `MATCHER=round_robin` rotates through available responders.

Evidence commands:

```powershell
findstr /n "RoundRobin" services\dispatch-service\app\matching.py
findstr /n "MATCHER" services\dispatch-service\app\matching.py
```

Document:

- Explain Strategy pattern.
- Explain why adding `round_robin` proves algorithms are interchangeable without changing `dispatch-service/app/main.py`.

### Re-run Baseline Test

Command:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

Then repeat signup, SOS, stats, and logs commands.

Document:

- Same evidence as the baseline smoke test.
- Mention that behavior still works after code changes.

---

## 6. Containerization

### Purpose

Create a production-style Dockerfile for each service instead of relying on Compose inline Dockerfiles.

### Why

Kubernetes deploys container images. Each service must have a repeatable image build process.

### Dockerfile Pattern

Each service should have:

```text
services/<service-name>/Dockerfile
```

Expected structure:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

EXPOSE <service-port>

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "<service-port>"]
```

Build commands:

```powershell
docker build -t helep/user-service:dev services/user-service
docker build -t helep/sos-service:dev services/sos-service
docker build -t helep/dispatch-service:dev services/dispatch-service
docker build -t helep/notification-service:dev services/notification-service
docker build -t helep/analytics-service:dev services/analytics-service
```

What these commands do:

- `docker build` creates a container image.
- `-t` gives the image a name and tag.
- The final path tells Docker where the build context is.

Expected output:

```text
Successfully tagged helep/user-service:dev
```

List images:

```powershell
docker images helep/*
```

Document:

- Dockerfile snippet.
- Successful image build output.
- Explain that each microservice is independently deployable.

---

## 7. Prepare Images for Minikube

### Purpose

Make the locally built images available to the Minikube cluster.

### Why

Minikube has its own Docker environment. If images are built in your normal Docker Desktop environment, Kubernetes inside Minikube may not see them.

### Use Minikube Docker Environment

Command:

```powershell
minikube -p minikube docker-env | Invoke-Expression
```

What this command does:

- Points your current PowerShell session at Minikube's Docker daemon.
- Images built after this command are available inside Minikube.

Rebuild images:

```powershell
docker build -t helep/user-service:dev services/user-service
docker build -t helep/sos-service:dev services/sos-service
docker build -t helep/dispatch-service:dev services/dispatch-service
docker build -t helep/notification-service:dev services/notification-service
docker build -t helep/analytics-service:dev services/analytics-service
```

Verify:

```powershell
docker images helep/*
```

Expected output:

```text
helep/user-service           dev
helep/sos-service            dev
helep/dispatch-service       dev
helep/notification-service   dev
helep/analytics-service      dev
```

Document:

- Explain the difference between local Docker and Minikube Docker.
- Capture `docker images helep/*`.

---

## 8. Strimzi Kafka on Kubernetes

### Purpose

Deploy Kafka in Kubernetes using Strimzi, as required by the project.

### Why

Docker Compose Kafka is only for development. Kubernetes submission should use a Kubernetes-native Kafka operator.

### Install Strimzi Operator

Commands:

```powershell
helm repo add strimzi https://strimzi.io/charts/
helm repo update
kubectl create namespace kafka
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator -n kafka
```

What these commands do:

- Adds the Strimzi Helm chart repository.
- Updates local Helm chart metadata.
- Creates a namespace for Kafka resources.
- Installs the Strimzi operator.

Expected output:

```text
STATUS: deployed
```

Verify:

```powershell
kubectl get pods -n kafka
```

Expected output:

```text
strimzi-cluster-operator-...   Running
```

### Create Kafka Cluster Manifest

Artifact:

```text
k8s/kafka/kafka.yaml
```

It should define a single-node Kafka cluster for local exercise use.

Apply:

```powershell
kubectl apply -f k8s/kafka/kafka.yaml
```

Verify:

```powershell
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

Expected output:

```text
helep-kafka   Ready
```

### Create Kafka Topics

Artifact:

```text
k8s/kafka/topics.yaml
```

Topics needed:

- `user.registered`
- `sos.triggered`
- `sos.cancelled`
- `responder.assigned`
- `responder.confirmed`
- `safety.zone.entered`
- `notification.sent`

Apply:

```powershell
kubectl apply -f k8s/kafka/topics.yaml
```

Verify:

```powershell
kubectl get kafkatopics -n kafka
```

Expected output:

```text
user.registered        Ready
sos.triggered          Ready
sos.cancelled          Ready
responder.assigned     Ready
responder.confirmed    Ready
safety.zone.entered    Ready
notification.sent      Ready
```

Document:

- Strimzi operator pod.
- Kafka cluster ready state.
- KafkaTopic list.
- Explain that explicit topics avoid relying on auto-create behavior.

### Troubleshooting: Kafka Pod ImagePullBackOff

What happened in this project:

The Kafka manifest was accepted, but the broker pod entered:

```text
ImagePullBackOff
```

The pod events showed:

```text
Failed to pull image "quay.io/strimzi/kafka:1.0.0-kafka-4.2.0"
net/http: TLS handshake timeout
```

What this means:

- The Strimzi operator and Kafka manifest were not the problem.
- Minikube could not download the Kafka image from `quay.io` during pod startup.
- This is a container image pull/network issue.

Fix used:

```powershell
minikube ssh -- docker pull quay.io/strimzi/kafka:1.0.0-kafka-4.2.0
kubectl delete pod helep-kafka-dual-role-0 -n kafka
kubectl get pods -n kafka -w
```

What the commands do:

- `minikube ssh -- docker pull ...` manually downloads the required Kafka image inside Minikube's Docker environment.
- `kubectl delete pod ...` removes the failed pod so Strimzi/Kubernetes can recreate it.
- `kubectl get pods -w` watches until the recreated pod becomes healthy.

Successful topic verification after the fix:

```powershell
kubectl get kafkatopics -n kafka
```

Observed result:

```text
NAME                  CLUSTER       PARTITIONS   REPLICATION FACTOR   READY
notification.sent     helep-kafka   3            1                    True
responder.assigned    helep-kafka   3            1                    True
responder.confirmed   helep-kafka   3            1                    True
safety.zone.entered   helep-kafka   3            1                    True
sos.cancelled         helep-kafka   3            1                    True
sos.triggered         helep-kafka   3            1                    True
user.registered       helep-kafka   3            1                    True
```

Google Doc note:

Record this under the "Strimzi Kafka Deployment" tab as a troubleshooting subsection. Explain that the first deployment failed because Minikube could not pull the Kafka image from Quay due to a TLS timeout, then show that manually pre-pulling the image resolved the issue. The final proof is that all seven Kafka topics became `READY=True`.

---

## 9. Helm Chart for HELEP

### Purpose

Package all HELEP Kubernetes resources into a repeatable Helm chart.

### Why

Helm makes the deployment reproducible and configurable. It also supports the project requirement for Kubernetes manifests and orchestration.

### Chart Structure

Create:

```text
charts/helep/
  Chart.yaml
  values.yaml
  templates/
```

Resources the chart should produce:

- ConfigMap for shared non-secret configuration.
- Secret for `JWT_SECRET`.
- Deployment for each service.
- Service for each service.
- PVC for each service database.
- HPA for each service.
- Ingress for HTTP routing.
- NetworkPolicy resources.
- Optional ServiceMonitor resources for Prometheus.

Files created for this project:

```text
charts/helep/Chart.yaml
charts/helep/values.yaml
charts/helep/templates/_helpers.tpl
charts/helep/templates/configmap.yaml
charts/helep/templates/secret.yaml
charts/helep/templates/pvc.yaml
charts/helep/templates/deployments.yaml
charts/helep/templates/services.yaml
charts/helep/templates/hpa.yaml
charts/helep/templates/ingress.yaml
charts/helep/templates/networkpolicy.yaml
charts/helep/templates/servicemonitor.yaml
```

Important chart defaults:

```yaml
global:
  kafkaBootstrap: helep-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
  imagePullPolicy: IfNotPresent
```

Why these defaults matter:

- `kafkaBootstrap` points HELEP services to the Strimzi Kafka bootstrap service.
- `IfNotPresent` lets Minikube use locally built images tagged as `helep/<service>:dev`.
- `serviceMonitor.enabled` is `false` by default so Helm works before Prometheus CRDs are installed.

### Values to Include

In `values.yaml`, include:

- image names and tags,
- service ports,
- replica counts,
- database mount paths,
- Kafka bootstrap address,
- JWT secret reference,
- resource requests and limits,
- HPA settings,
- ingress host.

Current service-to-image mapping:

```text
user-service         -> helep/user-service:dev         port 8001
sos-service          -> helep/sos-service:dev          port 8002
dispatch-service     -> helep/dispatch-service:dev     port 8003
notification-service -> helep/notification-service:dev port 8004
analytics-service    -> helep/analytics-service:dev    port 8005
```

Current ingress host mapping:

```text
user.helep.local         -> user-service
sos.helep.local          -> sos-service
dispatch.helep.local     -> dispatch-service
notification.helep.local -> notification-service
analytics.helep.local    -> analytics-service
```

### Validate the Chart

Commands:

```powershell
helm lint charts/helep
helm template helep charts/helep
```

What these commands do:

- `helm lint` checks chart structure and common errors.
- `helm template` renders Kubernetes YAML without applying it.

Expected output:

```text
1 chart(s) linted, 0 chart(s) failed
```

If `helm template` succeeds, it should print rendered YAML containing resources such as:

```text
kind: ConfigMap
kind: Secret
kind: PersistentVolumeClaim
kind: Deployment
kind: Service
kind: HorizontalPodAutoscaler
kind: Ingress
kind: NetworkPolicy
```

If validation fails:

- Read the first template error carefully.
- Fix the referenced file and line.
- Run `helm lint` again before attempting deployment.

### Deploy

Command:

```powershell
helm upgrade --install helep charts/helep -n helep --create-namespace
```

What this command does:

- Installs the chart if it does not exist.
- Upgrades it if it already exists.
- Deploys into namespace `helep`.
- Creates the namespace if missing.

Verify:

```powershell
kubectl get pods -n helep
kubectl get svc -n helep
kubectl get deploy -n helep
kubectl get pvc -n helep
kubectl get hpa -n helep
kubectl get networkpolicy -n helep
kubectl get ingress -n helep
```

Expected output:

```text
user-service-...           Running
sos-service-...            Running
dispatch-service-...       Running
notification-service-...   Running
analytics-service-...      Running
```

If pods show `ImagePullBackOff`:

- Confirm you built the images inside Minikube's Docker environment.
- Run:

```powershell
minikube -p minikube docker-env | Invoke-Expression
docker images helep/*
```

If the images are missing, rebuild them in that same PowerShell session.

Document:

- Helm lint success.
- Helm install/upgrade status.
- Kubernetes resource list.
- Explain why ConfigMaps, Secrets, PVCs, HPAs, and NetworkPolicies are used.

Google Doc body structure for this step:

```markdown
### Helm Chart Setup

The HELEP services were packaged as a Helm umbrella chart. This makes the Kubernetes deployment repeatable and lets environment-specific settings such as image tags, Kafka address, replica counts, and ingress hosts be changed from `values.yaml`.

### Resources Rendered

The chart renders Deployments, Services, PVCs, HPAs, an Ingress, ConfigMap, Secret, and NetworkPolicies for the five services.

### Commands and Results

Paste `helm lint`, `helm template`, and `helm upgrade --install` commands and the key success output.

### Evidence

Paste output from `kubectl get pods`, `kubectl get svc`, `kubectl get pvc`, `kubectl get hpa`, `kubectl get ingress`, and `kubectl get networkpolicy`.

### Justification

Helm improves repeatability and reduces deployment errors because the full microservice deployment is described as one versioned chart. ConfigMaps hold non-secret runtime configuration, Secrets protect JWT material, PVCs preserve SQLite files, HPAs support scalability, and NetworkPolicies reduce unnecessary pod communication.
```

---

## 10. Kubernetes Smoke Test

### Purpose

Prove that the Kubernetes deployment works end to end.

### Port Forward Services

Open separate terminals:

```powershell
kubectl port-forward -n helep svc/user-service 8001:8001
kubectl port-forward -n helep svc/sos-service 8002:8002
kubectl port-forward -n helep svc/analytics-service 8005:8005
```

What this does:

- Maps local ports to Kubernetes services.
- Allows you to test the app from your browser or terminal.

### Test Signup

PowerShell-native command:

```powershell
$signup = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8001/signup" `
  -ContentType "application/json" `
  -Body '{"phone":"+237600000002","password":"hunter22","role":"citizen"}'

$signup
$token = $signup.token
```

What this does:

- Sends a JSON signup request to `user-service`.
- Stores the JSON response in `$signup`.
- Extracts the JWT into `$token` for the SOS request.

Expected output:

```text
id                                    token
--                                    -----
<uuid>                                eyJ...
```

`curl.exe` alternative:

```powershell
curl.exe -X POST localhost:8001/signup -H "content-type: application/json" -d "{\"phone\":\"+237600000002\",\"password\":\"hunter22\",\"role\":\"citizen\"}"
```

Expected output:

```json
{"id":"...","token":"eyJ..."}
```

### Test SOS

PowerShell-native command:

```powershell
$headers = @{
  authorization = "Bearer $token"
}

$sos = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8002/sos" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"lat":4.0500,"lon":9.7700,"mode":"online"}'

$sos
$incidentId = $sos.incident_id
```

What this does:

- Sends an authenticated SOS request to `sos-service`.
- Uses the token returned from signup.
- Stores the incident response in `$sos`.
- Saves the incident id in `$incidentId` in case you need it later.

Expected output:

```text
incident_id                           status
-----------                           ------
<uuid>                                ACTIVE
```

`curl.exe` alternative:

```powershell
curl.exe -X POST localhost:8002/sos -H "authorization: Bearer <TOKEN>" -H "content-type: application/json" -d "{\"lat\":4.0500,\"lon\":9.7700,\"mode\":\"online\"}"
```

Expected output:

```json
{"incident_id":"...","status":"ACTIVE"}
```

### Test Analytics

PowerShell-native commands:

```powershell
Invoke-RestMethod -Uri "http://localhost:8005/stats/events"
Invoke-RestMethod -Uri "http://localhost:8005/stats/zones"
```

What these do:

- Query the analytics read model.
- Confirm that Kafka events reached `analytics-service`.
- Show event counts and danger-zone hit counts.

Expected output:

```text
stream               n
------               -
sos.triggered        1
responder.assigned   1
```

`curl.exe` alternatives:

```powershell
curl.exe localhost:8005/stats/events
curl.exe localhost:8005/stats/zones
```

Expected output:

```json
[{"stream":"sos.triggered","n":1}, ...]
```

### Check Logs

```powershell
kubectl logs -n helep deploy/dispatch-service
kubectl logs -n helep deploy/notification-service
kubectl logs -n helep deploy/analytics-service
```

Expected output:

```text
dispatch.assigned
notification.delivered
```

Document:

- Curl command results.
- Dispatch and notification logs.
- Explain that the same saga now works inside Kubernetes.

---

## 11. Monitoring with Prometheus and Grafana

### Purpose

Show observability for the deployed system.

### Why

The services already expose `/metrics`. Prometheus scrapes those metrics and Grafana visualizes them.

### Install Monitoring Stack

Commands:

```powershell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

Expected output:

```text
STATUS: deployed
```

Verify:

```powershell
kubectl get pods -n monitoring
```

Expected output:

```text
prometheus   Running
grafana      Running
```

### Access Grafana

Command:

```powershell
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Open:

```text
http://localhost:3000
```

Get Grafana password:

```powershell
kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | %{ [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
```

Document:

- Grafana login screenshot.
- Prometheus target screenshot.
- HELEP metric example.

Useful HELEP metrics:

- `helep_user_signups_total`
- `helep_sos_triggers_total`
- `helep_dispatch_assigned_total`
- `helep_notifications_sent_total`
- `helep_analytics_events_total`

Defense:

Monitoring supports reliability and operability because the team can detect whether services are alive and whether domain events are flowing.

---

## 12. Jenkins CI/CD

### Purpose

Create the required CI/CD pipeline using Jenkins.

### Why Jenkins

The project requirements mandate Jenkins. Jenkins will validate that the system can be built and Kubernetes manifests can be rendered.

Do not use GitHub Actions.

### Jenkinsfile Artifact

Create:

```text
Jenkinsfile
```

Recommended pipeline stages:

1. Checkout
2. Tool versions
3. Python syntax checks
4. Docker image builds
5. Helm lint
6. Helm template
7. Optional deploy to Minikube

Recommended Jenkinsfile outline:

```groovy
pipeline {
  agent any

  environment {
    IMAGE_TAG = "jenkins-${BUILD_NUMBER}"
  }

  stages {
    stage('Tool Versions') {
      steps {
        bat 'docker --version'
        bat 'kubectl version --client=true'
        bat 'helm version'
      }
    }

    stage('Python Syntax Checks') {
      steps {
        bat 'py -m py_compile services/user-service/app/main.py'
        bat 'py -m py_compile services/sos-service/app/main.py'
        bat 'py -m py_compile services/dispatch-service/app/main.py'
        bat 'py -m py_compile services/notification-service/app/main.py'
        bat 'py -m py_compile services/analytics-service/app/main.py'
      }
    }

    stage('Docker Build') {
      steps {
        bat 'docker build -t helep/user-service:%IMAGE_TAG% services/user-service'
        bat 'docker build -t helep/sos-service:%IMAGE_TAG% services/sos-service'
        bat 'docker build -t helep/dispatch-service:%IMAGE_TAG% services/dispatch-service'
        bat 'docker build -t helep/notification-service:%IMAGE_TAG% services/notification-service'
        bat 'docker build -t helep/analytics-service:%IMAGE_TAG% services/analytics-service'
      }
    }

    stage('Helm Validate') {
      steps {
        bat 'helm lint charts/helep'
        bat 'helm template helep charts/helep'
      }
    }
  }

  post {
    always {
      echo 'Pipeline finished. Check stage results above.'
    }
  }
}
```

### Create Jenkins Job

In Jenkins:

1. Open `http://localhost:8080`.
2. Create a new item.
3. Choose `Pipeline`.
4. Set pipeline definition to `Pipeline script from SCM`.
5. Choose Git.
6. Use your local or remote repository URL.
7. Set script path to `Jenkinsfile`.
8. Save.
9. Click `Build Now`.

### Expected Successful Output

```text
Tool Versions       SUCCESS
Python Syntax Checks SUCCESS
Docker Build        SUCCESS
Helm Validate       SUCCESS
Finished: SUCCESS
```

Document:

- Jenkins dashboard.
- Pipeline stage view.
- Console output showing Docker build and Helm validation.
- Explain that Jenkins provides repeatable CI/CD validation required by the project.

Optional deploy stage:

Only add deployment after the validation pipeline works. The deploy stage can run:

```powershell
helm upgrade --install helep charts/helep -n helep --create-namespace
```

Defense:

Keeping deployment optional reduces risk during the first CI setup. The mandatory proof is that Jenkins builds and validates the deployable artifacts.

### Troubleshooting: Jenkins Cannot Find `py`

Observed failure:

```text
'py' n'est pas reconnu en tant que commande interne
ou externe, un programme executable ou un fichier de commandes.
```

What this means:

- Jenkins successfully cloned the repository and started the pipeline.
- Git, Docker, `kubectl`, and Helm were available to Jenkins.
- The failure happened because Jenkins runs under a Windows service account whose PATH does not include the Python launcher `py`.

Fix used:

The `Jenkinsfile` was changed to use Dockerized Python instead of local Python:

```groovy
bat 'docker run --rm python:3.12-slim python --version'
bat 'docker run --rm -v "%CD%":/workspace -w /workspace python:3.12-slim python -m py_compile services/user-service/app/main.py services/user-service/app/db.py services/user-service/app/events.py'
```

Why this is better:

- Jenkins no longer depends on Python being installed in the service account PATH.
- The pipeline uses the same Docker runtime already required for building service images.
- The Python version is explicit and reproducible.

After applying the fix:

```powershell
git add Jenkinsfile
git commit -m "Use Dockerized Python checks in Jenkins pipeline"
git push origin main
```

Then rerun the Jenkins job or wait for the SCM polling trigger.

---

## 13. Design Process Document

### Purpose

Produce the L4 design process PDF from the provided template.

### Artifact

Input:

```text
design-process-template.md
```

Output:

```text
design-process.pdf
```

### Suggested Structure

#### 1. Project Specification

Write a short introduction:

```text
HELEP is an emergency response platform that allows citizens to trigger SOS incidents, dispatch responders, notify relevant users, and expose analytics for police or administrative users. The business value is faster emergency response, better incident visibility, and a scalable foundation for future safety features.
```

#### 2. Requirements Analysis

Use the SRS PDF as the authority. Fill functional requirements such as:

- user registration and authentication,
- SOS trigger,
- SOS cancellation,
- responder dispatch,
- alert notification,
- emergency contacts,
- analytics/statistics.

For each NFR, write a measurable acceptance criterion.

Example:

```text
Reliability: At least 99% of successfully accepted SOS events should result in either a responder assignment or a logged no-responder condition.
```

#### 3. Architectural Drivers and ASRs

Recommended top ASRs:

- Reliability: emergency workflows must not silently disappear.
- Availability: SOS submission should continue even when downstream consumers are temporarily busy.
- Scalability: Kafka topics and consumer groups allow services to scale independently.

#### 4. Component Identification

Map SRS components to services:

- User Management -> `user-service`
- Emergency Component -> `sos-service`
- Incident Response -> `sos-service` and `dispatch-service`
- Localization -> `dispatch-service`
- Alert Management -> `dispatch-service` and `notification-service`
- Analytics -> `analytics-service`

#### 5. Architectural Style

Defend:

- Microservices
- Event-driven architecture

Compare against:

- Monolith
- Layered architecture
- Synchronous service-to-service architecture

#### 6. Patterns Applied

Summarize:

- Saga
- Pub/Sub
- Repository
- Strategy
- Outbox-lite
- Circuit Breaker
- CQRS/read model
- Bulkhead via consumer groups or API Gateway via Ingress

#### 7. ADRs

Recommended ADRs:

```text
ADR-001: Use Kafka topic keying by incident_id
ADR-002: Use SQLite per service instead of shared database
ADR-003: Use Helm umbrella chart for Kubernetes deployment
```

#### 8. Trade-offs and Improvements

Mention:

- SQLite is simple but not ideal for production multi-writer scaling.
- Real SMS/media integrations are simulated.
- Local Minikube deployment differs from production HA clusters.

### Export PDF

Command:

```powershell
pandoc design-process-template.md -o design-process.pdf
```

Expected output:

```text
design-process.pdf created
```

Document:

- Final PDF filename.
- Short summary of what the design document proves.

---

## 14. Patterns-in-Code Document

### Purpose

Produce the L3 patterns PDF with code citations.

### Artifact

Input:

```text
patterns-template.md
```

Output:

```text
patterns.pdf
```

### Required Patterns

#### Choreographed Saga

Where:

- `sos-service/app/main.py`
- `dispatch-service/app/main.py`
- `notification-service/app/main.py`

What to explain:

- SOS trigger emits event.
- Dispatch assigns responder.
- Notification sends simulated message.
- Cancellation emits compensation event.

#### Pub/Sub

Where:

- every service's `app/events.py`

What to explain:

- Kafka topics decouple producers and consumers.
- Consumer groups allow scaling.
- Manual commit after handler success supports at-least-once processing.

#### Repository

Where:

- every service's `app/db.py`

What to explain:

- Database access is isolated from route handlers.
- Improves maintainability and testability.

#### Strategy

Where:

- `dispatch-service/app/matching.py`

What to explain:

- Matching algorithms are interchangeable using `MATCHER`.

#### Outbox-lite

Where:

- `sos-service/app/main.py`

What to explain:

- Service writes to DB then publishes event in the same request flow.
- It is "lite" because it does not use a durable outbox table and relay process.

#### Circuit Breaker

Where:

- every service's `app/events.py`

What to explain:

- Prevents repeated Kafka publish attempts during broker failure.
- Moves between CLOSED, OPEN, and HALF_OPEN.

#### Added Pattern 1: CQRS Read Model

Where:

- `analytics-service/app/main.py`
- `analytics-service/app/db.py`

What to explain:

- Write-side services emit events.
- Analytics builds read-optimized statistics.

#### Added Pattern 2: Bulkhead

Where:

- service-specific Kafka consumer groups.

What to explain:

- Each service consumes independently.
- Failure or slowness in analytics does not block notification or dispatch.

### Get Line Citations

Commands:

```powershell
findstr /n "async def trigger" services\sos-service\app\main.py
findstr /n "async def handle_sos" services\dispatch-service\app\main.py
findstr /n "async def on_event" services\notification-service\app\main.py
findstr /n "AIOKafkaConsumer" services\dispatch-service\app\events.py
findstr /n "class CircuitBreaker" services\user-service\app\events.py
findstr /n "class NearestMatcher" services\dispatch-service\app\matching.py
findstr /n "RoundRobin" services\dispatch-service\app\matching.py
```

### Export PDF

Command:

```powershell
pandoc patterns-template.md -o patterns.pdf
```

Document:

- PDF created.
- Pattern list.
- Code citations.

---

## 15. Demo Video Plan

### Purpose

The demo proves the submitted artifacts work.

### Recommended Flow

1. Show repository structure.
2. Show completed Dockerfiles, Helm chart, Kafka manifests, Jenkinsfile.
3. Show Jenkins successful pipeline.
4. Show Minikube cluster.
5. Show Strimzi Kafka running.
6. Show HELEP pods running.
7. Run signup request.
8. Run SOS trigger request.
9. Show dispatch and notification logs.
10. Show analytics endpoint.
11. Show Prometheus/Grafana metrics.
12. Summarize architecture decisions.

### Commands to Show in Demo

```powershell
kubectl get pods -n kafka
kubectl get kafkatopics -n kafka
kubectl get pods -n helep
kubectl get svc -n helep
kubectl get hpa -n helep
curl.exe localhost:8001/healthz
curl.exe localhost:8005/stats/events
kubectl logs -n helep deploy/notification-service
```

### Evidence to Capture

- Jenkins success screen.
- Kafka topic list.
- HELEP running pods.
- Successful API request.
- Notification logs.
- Analytics output.
- Grafana dashboard.

---

## 16. Final Submission Checklist

### Code Artifacts

- [ ] Circuit breaker completed in all service `events.py` files.
- [ ] Third dispatch strategy added.
- [ ] Dockerfile per service.
- [ ] Helm chart added.
- [ ] Strimzi Kafka manifest added.
- [ ] KafkaTopic manifests added.
- [ ] Kubernetes resources include Deployment, Service, ConfigMap, Secret, PVC, HPA, Ingress, NetworkPolicy.
- [ ] Jenkinsfile added.

### Documentation Artifacts

- [ ] `design-process.pdf`
- [ ] `patterns.pdf`
- [ ] Demo video
- [ ] Evidence screenshots/logs
- [ ] Google Doc completed with tabs/sections

### Validation Commands

```powershell
docker compose -f docker-compose.dev.yml up --build
helm lint charts/helep
helm template helep charts/helep
kubectl get pods -n kafka
kubectl get pods -n helep
kubectl get pods -n monitoring
```

### Final Defense Points

Use these in your oral or written defense:

- Kafka decouples emergency event producers from consumers.
- Saga choreography avoids a central orchestrator while preserving emergency workflow progress.
- `incident_id` keying preserves ordering for each incident.
- SQLite per service avoids a shared database anti-pattern.
- Repository pattern keeps persistence logic separate.
- Strategy pattern allows dispatch matching algorithms to change without rewriting the dispatch flow.
- Circuit breaker prevents repeated failed Kafka publish attempts.
- Helm makes Kubernetes deployment repeatable.
- Strimzi manages Kafka as a Kubernetes-native workload.
- Jenkins validates builds and deployment manifests as required by the project.

---

## 17. Chronological Order Summary

Follow this order:

1. Install missing tools.
2. Start Minikube and verify Kubernetes.
3. Run Docker Compose baseline smoke test.
4. Complete circuit breaker and third strategy.
5. Re-run Docker Compose smoke test.
6. Add Dockerfiles and build images.
7. Build images inside Minikube Docker environment.
8. Install Strimzi.
9. Deploy Kafka and Kafka topics.
10. Create and validate Helm chart.
11. Deploy HELEP to Kubernetes.
12. Run Kubernetes smoke test.
13. Install monitoring.
14. Capture Prometheus/Grafana evidence.
15. Configure Jenkins.
16. Add Jenkinsfile and run pipeline.
17. Fill design document.
18. Fill patterns document.
19. Export PDFs.
20. Record demo video.
21. Complete final submission checklist.

Some writing can happen in parallel while builds or deployments are running, but avoid starting Kubernetes deployment work before the Docker Compose baseline passes.

---

### Step 5 Code Explanations (Appended for Documentation)

**1. Circuit Breaker (pp/events.py in all 5 services)**
The circuit breaker prevents services from repeatedly trying to publish to Kafka when it is down, avoiding cascade failures.
We implemented three states:
- **CLOSED**: When ails < fail_threshold. Publishing is allowed.
- **OPEN**: When ails >= fail_threshold. Publishing is aggressively blocked to give the broker time to recover.
- **HALF_OPEN**: Using the eset_after_s timeout. If the circuit is OPEN but the 10-second timeout has passed, we return True to allow exactly one diagnostic attempt. If it succeeds, the breaker resets to CLOSED. If it fails, the timeout resets and it stays OPEN.

**2. Round Robin Dispatch Strategy (dispatch-service/app/matching.py)**
We added a third matching strategy called RoundRobinMatcher that satisfies the requirement to prove algorithms can be swapped without touching the main business logic (Strategy Pattern).
- It takes the iterable of responders, converts it to a list, and uses a rotating _index to pick a different responder for each request.
- The matcher() factory function was updated to return _rr_matcher when the MATCHER=round_robin environment variable is set.

**3. Containerization (Dockerfile for all 5 services)**
For Step 6, we created a single Dockerfile in each of the services/* directories (user-service, sos-service, dispatch-service, notification-service, analytics-service).
- Each Dockerfile uses python:3.12-slim as a lightweight base image.
- equirements.txt is copied and installed separately from the main pp/ folder to leverage Docker layer caching, significantly speeding up future rebuilds if only application code changes.
- The PYTHONUNBUFFERED=1 environment variable ensures that Python print statements and logs are sent straight to the terminal without being buffered, which is essential for observable log streams in Kubernetes.
- Finally, each Dockerfile exposes its respective service port (8001 through 8005) and spins up uvicorn bounded to  .0.0.0 so it can receive outside traffic.
