# K8s-Healer

K8s-Healer is a Python-based Kubernetes AI troubleshooting and safe remediation agent.

It connects to a Kubernetes cluster, checks workloads in the `agent` namespace, diagnoses common pod failures, and performs approved remediation actions only after explicit confirmation.

## Features

### Troubleshooting

The agent can:

- List pods and deployments
- Read pod logs
- Read previous container logs
- Read Kubernetes events
- Inspect container restart counts
- Inspect waiting reasons and exit codes
- Diagnose `ErrImagePull`
- Diagnose `ImagePullBackOff`
- Diagnose `CrashLoopBackOff`
- Suggest likely fixes

### Safe remediation

The agent currently supports:

- Updating a deployment image
- Scaling a deployment

Write actions follow this workflow:

```text
User request
    ↓
Python shows the proposed change
    ↓
User types CONFIRM
    ↓
Python applies the change
    ↓
Python verifies deployment status

The LLM helps with troubleshooting. Python controls Kubernetes write operations.

Tech Stack
Python
LangChain
Ollama
Qwen 2.5 1.5B
Kubernetes Python Client
Kubernetes / Kind
Project Structure
k8s-healer/
├── agent/
│   └── agent.py
├── cluster/
│   └── client.py
├── config/
│   └── settings.py
├── tools/
│   ├── deployment_tools.py
│   ├── event_tools.py
│   ├── log_tools.py
│   ├── pod_tools.py
│   └── remediation_tools.py
├── workflows/
│   └── pod_troubleshooter.py
├── app.py
├── requirements.txt
└── README.md
Prerequisites

Install the following on Linux:

Python 3.10 or newer
kubectl
A Kubernetes cluster such as Kind, Minikube, EKS, or Kubernetes on EC2
Ollama

Check Python:

python3 --version

Check Kubernetes access:

kubectl get nodes

Create the required namespace if it does not exist:

kubectl create namespace agent

Check Ollama:

ollama --version

Pull the model:

ollama pull qwen2.5:1.5b

Verify the model:

ollama list
Installation

Clone the repository:

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd k8s-healer

Create a virtual environment:

python3 -m venv venv

Activate it:

source venv/bin/activate

Install dependencies:

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Configuration

Create the environment file:

touch .env
nano .env

Add:

K8S_NAMESPACE=agent
OLLAMA_MODEL=qwen2.5:1.5b

Save the file with:

Ctrl + O
Enter
Ctrl + X
Run the Agent

Activate the virtual environment:

source venv/bin/activate

Start the agent:

python app.py

Expected output:

Kubernetes AI Agent started
Namespace: agent
Model: qwen2.5:1.5b
Type exit to quit

Exit the agent:

exit
Usage
List Pods
List all pods
List Deployments
Show deployments
Diagnose a Failing Pod

First get the pod name:

kubectl get pods -n agent

Then ask the agent:

Use kubernetes_troubleshoot_pod with pod_name "POD_NAME" and explain the root cause.

Example:

Use kubernetes_troubleshoot_pod with pod_name "broken-image-586f9bd7bf-abcde" and explain the root cause.
Fix a Deployment Image
Fix deployment broken-image by changing its image to nginx:latest

The application shows a proposed change.

Apply it:

CONFIRM
Scale a Deployment
Scale deployment test-nginx to 3 replicas

The application shows a proposed scale operation.

Apply it:

CONFIRM
Verify Kubernetes Changes

Check pods:

kubectl get pods -n agent

Watch pods while Kubernetes creates or replaces them:

kubectl get pods -n agent -w

Check deployments:

kubectl get deployments -n agent

Describe a deployment:

kubectl describe deployment DEPLOYMENT_NAME -n agent
Testing
Test ImagePullBackOff

Create a deployment with an invalid image tag:

kubectl create deployment broken-image \
  --image=nginx:this-tag-does-not-exist \
  -n agent

Check the pod:

kubectl get pods -n agent

Expected status:

ImagePullBackOff

Get the exact pod name, then ask:

Use kubernetes_troubleshoot_pod with pod_name "BROKEN_POD_NAME" and explain the root cause.

Fix it:

Fix deployment broken-image by changing its image to nginx:latest

Then approve:

CONFIRM
Test CrashLoopBackOff

Create a deployment that exits with code 1:

kubectl create deployment crash-app \
  --image=busybox \
  -n agent \
  -- sh -c "exit 1"

Check the pod:

kubectl get pods -n agent

Expected status:

CrashLoopBackOff

Get the exact pod name, then ask:

Use kubernetes_troubleshoot_pod with pod_name "CRASH_POD_NAME" and explain the root cause.
Cleanup

Delete test deployments:

kubectl delete deployment broken-image crash-app -n agent --ignore-not-found

Check remaining pods:

kubectl get pods -n agent
Safety Design

K8s-Healer separates AI reasoning from Kubernetes modifications.

The LLM can:

Inspect cluster state
Read logs and events
Explain failures
Suggest fixes

Python applies write actions only after the user enters:

CONFIRM

This prevents unapproved scaling or image changes.

Current Limitations
Works with one configured namespace: agent
Confirmation state is stored only while app.py is running
Uses the local qwen2.5:1.5b model
Supports image updates and scaling only
No persistent audit log yet
Future Improvements
Restart deployment with confirmation
Rollback deployment
Automatic rollout monitoring
Audit logging
Prometheus integration
Grafana alerts
Slack notifications
Web dashboard
Multi-namespace support
RBAC and production approval workflows
Author

Praveen Singh Tomar
Aspiring DevOps and Cloud Engineer