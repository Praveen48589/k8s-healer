from cluster.client import core_v1
from config.settings import DEFAULT_NAMESPACE


def list_pods(namespace: str = DEFAULT_NAMESPACE) -> list[dict]:
    pods = core_v1.list_namespaced_pod(namespace=namespace)

    return [
        {
            "name": pod.metadata.name,
            "status": pod.status.phase,
        }
        for pod in pods.items
    ]