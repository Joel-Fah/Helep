# HELEP L4 Design Process Document

## 1. Project Specification

HELEP is an emergency response platform for citizens, responders, police, and administrators. Citizens can register, authenticate, manage emergency contacts, and trigger an SOS with location and simulated media metadata. The system dispatches responders, sends simulated notifications, and exposes analytics for police visibility. The business value is faster emergency escalation, auditable incident handling, and a scalable service foundation that can later integrate real SMS, GPS, and media providers.

The implemented architecture uses five FastAPI microservices, Apache Kafka for asynchronous event flow, SQLite-per-service persistence, Docker containers, Kubernetes orchestration, Helm packaging, Strimzi-managed Kafka, Prometheus/Grafana monitoring, and Jenkins CI/CD.

## 2. Requirements Analysis

### 2.1 Functional Requirements

| # | Requirement | Implementation Evidence |
|---|-------------|-------------------------|
| F1 | Citizens, responders, and police users can register and authenticate. | `user-service` exposes `/signup`, `/login`, `/me`, and JWT-based auth. |
| F2 | Users can manage emergency contacts. | `user-service` exposes `/contacts` endpoints backed by SQLite. |
| F3 | Citizens can trigger SOS incidents with location and mode. | `sos-service` exposes `POST /sos`, stores incidents, and emits `sos.triggered`. |
| F4 | Citizens can cancel active SOS incidents. | `sos-service` exposes `POST /sos/{id}/cancel` and emits `sos.cancelled`. |
| F5 | The platform assigns an available responder. | `dispatch-service` consumes `sos.triggered`, reserves a free responder, and emits `responder.assigned`. |
| F6 | The platform prevents double dispatch for one incident. | `assignments.incident_id` is the primary key and responder claims are atomic. |
| F7 | The platform notifies users/responders. | `notification-service` consumes dispatch and zone events, persists notifications, logs simulated delivery, and emits `notification.sent`. |
| F8 | Police/admin users can view incident statistics. | `analytics-service` consumes all event streams and exposes `/stats/events`, `/stats/zones`, and `/stats/crime`. |

### 2.2 Non-Functional Requirements

| Quality Attribute | Acceptance Criterion | Architectural Response |
|------------------|----------------------|------------------------|
| Availability | Core service pods expose health and readiness endpoints and can be restarted independently. | Kubernetes Deployments, `/healthz`, `/readyz`, and event-driven decoupling. |
| Reliability | A consumed Kafka event is committed only after handler success. | Manual Kafka commits after successful handling in `events.py`. |
| Scalability | Services can scale independently and Kafka topics use three partitions. | Kubernetes HPAs and KafkaTopic resources with three partitions. |
| Confidentiality | JWT signing material is not stored in plain ConfigMaps. | Helm renders `JWT_SECRET` as a Kubernetes Secret. |
| Integrity | One responder assignment is allowed per incident. | SQLite primary key on `assignments.incident_id` and atomic responder update. |
| Usability | Core flows are exposed through simple HTTP JSON endpoints. | FastAPI endpoints for signup, SOS, contacts, notifications, and analytics. |
| Observability | Services expose Prometheus metrics. | `/metrics` endpoint on every service and lightweight Prometheus/Grafana setup. |
| Portability | The system can be rebuilt and deployed consistently. | Dockerfiles, Helm chart, and Jenkins pipeline validation. |

### 2.3 Constraints

| Constraint | Risk | Mitigation |
|------------|------|------------|
| Only one responder should handle an SOS at a time. | Duplicate dispatch could confuse field response. | `dispatch-service` uses a primary key assignment row and atomic responder busy flag. |
| SOS notification must be fast. | Synchronous fan-out could slow user requests. | Kafka decouples SOS creation from dispatch, notification, and analytics processing. |
| Kubernetes orchestration is required. | Manual manifests are error-prone. | Helm chart packages all HELEP Kubernetes resources. |
| Kafka must be Kubernetes-native. | Docker Compose Kafka is not a valid final deployment. | Strimzi deploys and manages Kafka inside Kubernetes. |
| Jenkins is mandatory for CI/CD. | GitHub Actions would not satisfy the requirement. | Jenkinsfile validates code, builds images, and validates Helm. |

## 3. Architectural Drivers and ASRs

### ASR 1: Reliable Emergency Event Flow

Emergency events must not silently disappear. The architecture uses Kafka topics, explicit event streams, consumer groups, and manual commit behavior so failed handlers do not acknowledge messages prematurely.

### ASR 2: Independent Scalability

Dispatch, notification, and analytics have different workloads. Microservices and Kafka consumer groups allow each service to scale independently while preserving topic-level event flow.

### ASR 3: Deployment Repeatability

The project requires orchestration evidence. Dockerfiles, Helm, Strimzi resources, and Jenkins validation make deployment repeatable and defensible.

## 4. Component Identification

### 4.1 SRS Components

The SRS-level components are represented as user management, emergency/SOS handling, incident response, localization, alert management, notification delivery, feedback/review, and analytics/statistics.

### 4.2 Service Decomposition

| SRS Area | Implemented Service | Justification |
|----------|---------------------|---------------|
| User Management | `user-service` | Keeps identity, JWT, credibility, and contacts isolated. |
| Emergency Component | `sos-service` | Owns SOS trigger/cancel lifecycle and incident state. |
| Incident Response | `sos-service` + `dispatch-service` | SOS creation and responder assignment are separate responsibilities. |
| Localization | `dispatch-service` | Matching uses location and responder availability. |
| Alert Management | `dispatch-service` + `notification-service` | Dispatch decides what happened; notification handles delivery. |
| Analytics | `analytics-service` | Builds a read model from event streams for police/admin use. |
| Feedback/Review | Out of scope | Not required for the minimal 24-hour implementation. |

## 5. Architectural Style

### Chosen Style: Microservices + Event-Driven Architecture

Microservices are appropriate because the system has clear service boundaries: identity, SOS incidents, dispatch, notifications, and analytics. Event-driven architecture is appropriate because emergency workflows involve multiple downstream reactions that should not block the initial SOS request.

### Alternative 1: Monolith

A monolith would be simpler to deploy at first, but it would weaken independent scalability and fault isolation. Notification or analytics failures could more easily affect SOS handling unless carefully isolated internally.

### Alternative 2: Synchronous Service-to-Service Architecture

Synchronous HTTP fan-out would make the flow easier to trace, but each SOS request would depend on dispatch, notification, and analytics being available at the same time. Kafka avoids this by allowing downstream consumers to process events asynchronously.

## 6. Architectural Patterns Applied

| Pattern | Location | Problem Solved |
|---------|----------|----------------|
| Choreographed Saga | `sos-service/app/main.py`, `dispatch-service/app/main.py`, `notification-service/app/main.py` | Coordinates SOS, dispatch, notification, and cancellation without a central orchestrator. |
| Pub/Sub | all service `app/events.py` files | Decouples services through Kafka topics and consumer groups. |
| Repository | all service `app/db.py` files | Keeps SQL persistence separate from route/event logic. |
| Strategy | `dispatch-service/app/matching.py` | Allows responder matching algorithms to change through `MATCHER`. |
| Outbox-lite | `sos-service/app/main.py` | Writes incident state then publishes a Kafka event in one request flow. |
| Circuit Breaker | all service `app/events.py` files | Stops repeated Kafka publish attempts after failures. |
| CQRS Read Model | `analytics-service/app/main.py` and `app/db.py` | Builds query-optimized statistics from events. |
| Bulkhead | service-specific Kafka consumer groups | Keeps failures in one consumer group from blocking others. |

## 7. Architecture Decision Records

### ADR-001: Use Kafka Topic Keying by Incident ID

#### Context

SOS events, cancellation events, responder assignment events, and notification events are part of one incident workflow.

#### Decision

Saga-critical events are published with the incident ID as the Kafka key.

#### Consequences

Events for the same incident are routed to the same partition, preserving order for that incident. This supports the no-double-dispatch invariant when consumers scale horizontally.

#### Alternatives Considered

Random partitioning was simpler but could reorder incident events. Synchronous HTTP calls would avoid partitioning concerns but would reduce availability and decoupling.

### ADR-002: Use SQLite Per Service Instead of a Shared Database

#### Context

The project is a 24-hour orchestration exercise with a microservice architecture.

#### Decision

Each service owns its own SQLite database file mounted through a Kubernetes PVC.

#### Consequences

This avoids a shared database anti-pattern and keeps service ownership clear. SQLite is not ideal for production multi-writer scaling, but it is suitable for the exercise scope and local demo.

#### Alternatives Considered

A shared PostgreSQL database would be more production-like, but it would blur service boundaries and add operational weight.

### ADR-003: Use a Helm Umbrella Chart

#### Context

The project requires many Kubernetes resources across five services.

#### Decision

Use one Helm chart under `charts/helep` to render Deployments, Services, PVCs, HPAs, Ingress, ConfigMap, Secret, NetworkPolicies, and optional ServiceMonitor resources.

#### Consequences

Deployment is repeatable and values-driven. Helm validation can be included in Jenkins. The trade-off is that students must understand template rendering and values structure.

#### Alternatives Considered

Raw YAML manifests would be more direct, but harder to keep consistent across five services.

## 8. Trade-Offs and Improvement Perspectives

1. SQLite is acceptable for a local orchestration exercise, but a production system should use a managed database per service or another durable store with stronger concurrency behavior.
2. Notification and media capture are simulated. Production would need SMS/push provider integrations, retry policies, provider credentials, and secure object storage.
3. The local Minikube deployment is not highly available. A production deployment should use multi-node Kubernetes, persistent Kafka storage, multiple Kafka brokers, and external monitoring retention.

## 9. Submission Checklist

- [ ] Dockerfiles for all services.
- [ ] Strimzi Kafka manifests.
- [ ] KafkaTopic manifests.
- [ ] Helm chart.
- [ ] ConfigMap, Secret, PVC, Deployment, Service, Ingress, HPA, and NetworkPolicy evidence.
- [ ] Prometheus/Grafana or `/metrics` evidence.
- [ ] Jenkins successful pipeline screenshot/output.
- [ ] `patterns.pdf`.
- [ ] `design-process.pdf`.
- [ ] Demo video.
