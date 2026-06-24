from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from tools.event_tools import get_pod_events
from workflows.pod_troubleshooter import troubleshoot_pod

from config.settings import DEFAULT_NAMESPACE, OLLAMA_MODEL
from tools.deployment_tools import list_deployments, scale_deployment
from tools.log_tools import get_pod_logs
from tools.pod_tools import list_pods


@tool
def kubernetes_list_pods(namespace: str = DEFAULT_NAMESPACE) -> list[dict]:
    """List Kubernetes pods. Default namespace is agent."""
    return list_pods(namespace)


@tool
def kubernetes_get_pod_logs(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    """Get the last 100 log lines from a Kubernetes pod."""
    return get_pod_logs(pod_name, namespace)


@tool
def kubernetes_list_deployments(
    namespace: str = DEFAULT_NAMESPACE,
) -> list[dict]:
    """List Kubernetes deployments and replica counts."""
    return list_deployments(namespace)


@tool
def kubernetes_scale_deployment(
    deployment_name: str,
    replicas: int,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    """Scale a deployment only when the user explicitly asks."""
    return scale_deployment(deployment_name, replicas, namespace)

@tool
def kubernetes_get_pod_events(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> list[dict]:
    """Get Kubernetes events for one pod."""
    return get_pod_events(pod_name, namespace)


@tool
def kubernetes_troubleshoot_pod(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> dict:
    """
    Inspect a pod, its Kubernetes events, and its logs.
    Use this when a user asks why a specific pod is failing.
    """
    return troubleshoot_pod(pod_name, namespace)    

def build_agent():
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0,
    )

    return create_agent(
        model=llm,
        tools=[
            kubernetes_list_pods,
            kubernetes_get_pod_logs,
            kubernetes_list_deployments,
            kubernetes_scale_deployment,
            kubernetes_get_pod_events,
            kubernetes_troubleshoot_pod 
        ],
        system_prompt=(
            f"You are a Kubernetes AI agent. "
            f"Default namespace is '{DEFAULT_NAMESPACE}'. "
            "Use tools to inspect Kubernetes before answering. "
            "Do not invent pod names or status. "
            "Only scale when the user explicitly requests it."
            "For a failing pod, use kubernetes_troubleshoot_pod before explaining the cause. "
            "Do not create, delete, restart, or modify resources unless the user explicitly asks."
            "For CrashLoopBackOff, use previous_logs as the primary evidence for why the last container instance exited. "
        ),
    )
