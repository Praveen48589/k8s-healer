from cluster.client import core_v1
from config.settings import DEFAULT_NAMESPACE


def list_pods(namespace: str = DEFAULT_NAMESPACE) -> list[dict]:
    pods = core_v1.list_namespaced_pod(namespace=namespace)

    result = []

    for pod in pods.items:
        statuses = pod.status.container_statuses or []

        restarts = sum(item.restart_count for item in statuses)

        waiting_reasons = [
            item.state.waiting.reason
            for item in statuses
            if item.state.waiting and item.state.waiting.reason
        ]

        terminated_reasons = [
            item.state.terminated.reason
            for item in statuses
            if item.state.terminated and item.state.terminated.reason
        ]

        result.append(
            {
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "restarts": restarts,
                "waiting_reasons": waiting_reasons,
                "terminated_reasons": terminated_reasons,
            }
        )

    return result