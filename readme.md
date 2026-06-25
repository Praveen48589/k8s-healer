# K8s-Healer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/Kind-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kind" />
</p>

<p align="center">
  <b>A Python-based Kubernetes troubleshooting and safe remediation agent powered by a local LLM.</b>
</p>

---

## Overview

K8s-Healer helps diagnose common Kubernetes workload failures and safely perform selected remediation actions.

It uses a local Ollama model to explain Kubernetes issues, while Python code collects deterministic cluster data such as pod events, logs, container status, restart counts, and exit codes.

For safety, Kubernetes write operations are not directly controlled by the LLM. The application first proposes a change, waits for explicit confirmation, then applies and verifies the change.

---

## Key Features

### Troubleshooting

* List pods and deployments in the configured namespace
* Read pod logs and previous container logs
* Read Kubernetes events
* Inspect pod phase, restart counts, waiting reasons, and exit codes
* Diagnose common failures:

  * `ErrImagePull`
  * `ImagePullBackOff`
  * `CrashLoopBackOff`
  * Invalid image tags
  * Container startup failures

### Safe Remediation

* Update a deployment image
* Scale a deployment
* Require explicit confirmation before any change
* Verify deployment status after a change

### Safety Workflow

```text
User request
    ↓
Application proposes the Kubernetes change
    ↓
User reviews and types CONFIRM
    ↓
Python applies the exact stored change
    ↓
Application checks deployment status
```

---

## Architecture

```text
User
  │
  ▼
CLI Application (app.py)
  │
  ├── Read-only requests ──► LangChain + Ollama
  │                              │
  │                              ▼
  │                        Kubernetes tools
  │                        - Pods
  │                        - Logs
  │                        - Events
  │                        - Deployments
  │
  └── Write requests ─────► Python confirmation workflow
                                 │
                                 ▼
                           Kubernetes Python Client
```

---

## Tech Stack

| Technology               | Purpose                              |
| ------------------------ | ------------------------------------ |
| Python                   | Main application language            |
| Kubernetes Python Client | Kubernetes API communication         |
| LangChain                | Agent and tool orchestration         |
| Ollama                   | Local LLM runtime                    |
| Qwen 2.5 1.5B            | Local model used by the agent        |
| Kind                     | Local Kubernetes cluster for testing |
| Linux                    | Development and runtime environment  |

---

## Project Structure

```text
k8s-healer/
├── agent/
│   └── agent.py                 # LangChain agent configuration
├── cluster/
│   └── client.py                # Kubernetes API client setup
├── config/
│   └── settings.py              # Namespace and model configuration
├── tools/
│   ├── deployment_tools.py      # Deployment operations
│   ├── event_tools.py           # Pod event collection
│   ├── log_tools.py             # Current and previous pod logs
│   ├── pod_tools.py             # Pod inspection
│   └── remediation_tools.py     # Image update and verification
├── workflows/
│   └── pod_troubleshooter.py    # Pod troubleshooting workflow
├── app.py                       # CLI entry point
├── requirements.txt
└── README.md
```

---

## Prerequisites

Install the following on Linux:

* Python 3.10 or later
* `kubectl`
* Ollama
* A Kubernetes cluster, such as Kind, Minikube, EKS, or a self-managed cluster

Check Python:

```bash
python3 --version
```

Check Kubernetes access:

```bash
kubectl get nodes
```

Check Ollama:

```bash
ollama --version
```

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd k8s-healer
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Pull the local model

```bash
ollama pull qwen2.5:1.5b
```

Verify:

```bash
ollama list
```

---

## Kubernetes Setup

This project uses the `agent` namespace.

Create it if it does not already exist:

```bash
kubectl create namespace agent
```

Verify:

```bash
kubectl get namespaces
```

---

## Configuration

Create a `.env` file in the project root:

```bash
touch .env
nano .env
```

Add:

```env
K8S_NAMESPACE=agent
OLLAMA_MODEL=qwen2.5:1.5b
```

Save in Nano:

```text
Ctrl + O
Enter
Ctrl + X
```

---

## Run the Agent

Activate the virtual environment:

```bash
source venv/bin/activate
```

Start the application:

```bash
python app.py
```

Expected output:

```text
Kubernetes AI Agent started
Namespace: agent
Model: qwen2.5:1.5b
Type exit to quit
```

To stop the application:

```text
exit
```

---

## Usage Examples

### Diagnose a Pod

First, find the pod name:

```bash
kubectl get pods -n agent
```

Then ask:

```text
Use kubernetes_troubleshoot_pod with pod_name "POD_NAME" and explain the root cause.
```

---

### Fix an Invalid Image

```text
Fix deployment broken-image by changing its image to nginx:latest
```

The application will display a proposal similar to:

```text
Proposed image update:
Deployment: broken-image
Namespace: agent
New image: nginx:latest

No change has been made.
Type exactly CONFIRM to apply this image update.
```

Apply it:

```text
CONFIRM
```

---

### Scale a Deployment

```text
Scale deployment test-nginx to 3 replicas
```

The application will display a proposed scale operation.

Apply it:

```text
CONFIRM
```

Verify:

```bash
kubectl get deployments -n agent
kubectl get pods -n agent
```

---

## Testing

### Test `ImagePullBackOff`

Create a deployment with a non-existent image tag:

```bash
kubectl create deployment broken-image \
  --image=nginx:this-tag-does-not-exist \
  -n agent
```

Check the pod status:

```bash
kubectl get pods -n agent
```

Then diagnose it through the agent.

Fix it with:

```text
Fix deployment broken-image by changing its image to nginx:latest
```

Then confirm:

```text
CONFIRM
```

---

### Test `CrashLoopBackOff`

Create a deployment that exits immediately:

```bash
kubectl create deployment crash-app \
  --image=busybox \
  -n agent \
  -- sh -c "exit 1"
```

Check the pod:

```bash
kubectl get pods -n agent
```

Diagnose it:

```text
Use kubernetes_troubleshoot_pod with pod_name "CRASH_POD_NAME" and explain the root cause.
```

---

## Cleanup

Remove test deployments:

```bash
kubectl delete deployment broken-image crash-app -n agent --ignore-not-found
```

Check remaining pods:

```bash
kubectl get pods -n agent
```

---

## Current Limitations

* Works with one configured namespace: `agent`
* Confirmation state exists only while the application is running
* Uses a small local model, so explanations can occasionally be generic
* Current write actions are limited to image updates and scaling
* No persistent audit log yet

---

## Future Improvements

* Deployment restart with confirmation
* Deployment rollback with confirmation
* Rollout monitoring and timeout detection
* Persistent audit logs
* Prometheus and Grafana integration
* Slack notifications
* Web dashboard
* Multi-namespace support
* RBAC and production approval workflows

---

## Author

**Praveen Singh Tomar**
Aspiring DevOps and Cloud Engineer
