# HELEP Demo Guidelines

Target length: 2 to 3 minutes.

Keep the video tight. Do not explain installation, file structure, templates, or long configuration details. The goal is to prove the required runtime behavior.

## Before Recording

Start from this state:

- Minikube is running.
- Kafka/Strimzi is running.
- HELEP is already deployed.
- Monitoring is already deployed.
- Jenkins already has a green build.
- You have three terminals ready:
  - Terminal 1: Kubernetes checks and chaos command.
  - Terminal 2: API commands.
  - Terminal 3: logs.
- Browser tabs ready:
  - Grafana dashboard.
  - Jenkins successful pipeline run.

Quick pre-check:

```powershell
kubectl get pods -n kafka
kubectl get pods -n helep
kubectl get pods -n monitoring
```

## Video Flow

### 1. Kubernetes Resources

Show:

```powershell
kubectl get all -n helep
kubectl get pv,pvc -n helep
```

Say briefly:

```text
The HELEP namespace contains the five deployed services, Kubernetes Services, HPAs, and persistent storage claims for per-service SQLite data.
```

### 2. Trigger a Full SOS

Start port-forwards before recording, or show them quickly if time allows:

```powershell
kubectl port-forward -n helep svc/user-service 8001:8001
kubectl port-forward -n helep svc/sos-service 8002:8002
kubectl port-forward -n helep svc/analytics-service 8005:8005
```

Register a fresh user:

```powershell
curl.exe -s -X POST http://localhost:8001/signup -H "content-type: application/json" -d "{\"phone\":\"+237600000101\",\"password\":\"hunter22\",\"role\":\"citizen\"}"
```

Copy the returned token into:

```powershell
$TOKEN = "<paste-token-here>"
```

Trigger SOS:

```powershell
curl.exe -s -X POST http://localhost:8002/sos -H "authorization: Bearer $TOKEN" -H "content-type: application/json" -d "{\"lat\":4.0500,\"lon\":9.7700,\"mode\":\"online\"}"
```

Copy the returned `incident_id` into:

```powershell
$INCIDENT = "<paste-incident-id-here>"
```

Tail notification logs:

```powershell
kubectl logs -n helep deploy/notification-service --tail=50
```

Say briefly:

```text
The SOS request creates an incident, Kafka carries the event, dispatch assigns a responder, and notification-service records simulated delivery.
```

### 3. Cancel SOS and Show Responder Released

Cancel the incident:

```powershell
curl.exe -s -X POST "http://localhost:8002/sos/$INCIDENT/cancel" -H "authorization: Bearer $TOKEN"
```

Show dispatch logs:

```powershell
kubectl logs -n helep deploy/dispatch-service --tail=80
```

Look for release/cancellation evidence. If logs are sparse, also show analytics:

```powershell
curl.exe -s http://localhost:8005/stats/events
```

Say briefly:

```text
Cancellation emits `sos.cancelled`; dispatch handles the compensation step and releases the responder assignment.
```

### 4. Chaos Test: Delete Dispatch Pod

Delete the dispatch pod:

```powershell
kubectl delete pod -n helep -l app=dispatch-service
```

Show Kubernetes recreating it:

```powershell
kubectl get pods -n helep -w
```

After the new dispatch pod is running, trigger another SOS with a fresh phone number:

```powershell
curl.exe -s -X POST http://localhost:8001/signup -H "content-type: application/json" -d "{\"phone\":\"+237600000102\",\"password\":\"hunter22\",\"role\":\"citizen\"}"
```

Set the new token:

```powershell
$TOKEN2 = "<paste-new-token-here>"
```

Trigger SOS:

```powershell
curl.exe -s -X POST http://localhost:8002/sos -H "authorization: Bearer $TOKEN2" -H "content-type: application/json" -d "{\"lat\":4.0500,\"lon\":9.7700,\"mode\":\"online\"}"
```

Show dispatch and notification evidence:

```powershell
kubectl logs -n helep deploy/dispatch-service --tail=80
kubectl logs -n helep deploy/notification-service --tail=80
```

Say briefly:

```text
Deleting the dispatch pod simulates failure. Kubernetes recreates the pod, Kafka consumer group membership rebalances, and uncommitted work can be re-delivered, so the saga continues after recovery.
```

### 5. Grafana Metrics

Switch to Grafana.

Show a dashboard or panel with at least one non-zero HELEP metric, such as:

```text
helep_user_signups_total
helep_sos_triggers_total
helep_dispatch_assigned_total
helep_notifications_sent_total
helep_analytics_events_total
```

Say briefly:

```text
The metrics are non-zero after the demo flow, proving that the services expose Prometheus-compatible metrics and Grafana can visualize them.
```

### 6. Jenkins Green Run

Switch to Jenkins.

Show the latest successful run with:

```text
Finished: SUCCESS
```

Highlight stages:

```text
Tool Versions
Python Syntax Checks
Docker Build
Helm Validate
```

Say briefly:

```text
Jenkins polls the main branch and validates the project by compiling Python files in Docker, building all five service images, and validating the Helm chart.
```

## Closing Line

End with:

```text
This demo showed the Kubernetes deployment, persistent storage, complete SOS saga, cancellation compensation, dispatch recovery after pod deletion, non-zero Grafana metrics, and a green Jenkins CI/CD pipeline.
```

## Timing Guide

- Kubernetes resources: 20 seconds
- Full SOS: 35 seconds
- Cancel SOS: 25 seconds
- Chaos test: 40 seconds
- Grafana: 20 seconds
- Jenkins: 20 seconds

Total: about 2 minutes 40 seconds.

## If Something Is Slow

Do not wait too long on camera.

If `kubectl get pods -w` takes time, say:

```text
While Kubernetes recreates the dispatch pod, I will continue once it reaches Running.
```

Pause recording if possible, then resume when ready.

If Grafana is slow, show Prometheus or direct metrics instead:

```powershell
curl.exe -s http://localhost:8001/metrics
curl.exe -s http://localhost:8002/metrics
```
