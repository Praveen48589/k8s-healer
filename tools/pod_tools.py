from cluster.client import core_v1
from config.settings import DEFAULT_NAMESPACE


def list_pods(namespace: str = DEFAULT_NAMESPACE) -> list[dict]:
    pods = core_v1.list_namespaced_pod(namespace=namespace)

    result = []

    for pod in pods.items:
        statuses = pod.status.container_statuses or []

        containers = []

        for index, container in enumerate(pod.spec.containers):
            status = statuses[index] if index < len(statuses) else None

            waiting_reason = None
            last_exit_code = None
            last_terminated_reason = None

            if status and status.state.waiting:
                waiting_reason = status.state.waiting.reason

            if status and status.last_state.terminated:
                last_exit_code = status.last_state.terminated.exit_code
                last_terminated_reason = status.last_state.terminated.reason

            containers.append(
                {
                    "name": container.name,
                    "image": container.image,
                    "command": container.command or [],
                    "args": container.args or [],
                    "waiting_reason": waiting_reason,
                    "last_exit_code": last_exit_code,
                    "last_terminated_reason": last_terminated_reason,
                    "restarts": status.restart_count if status else 0,
                }
            )

        result.append(
            {
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "containers": containers,
            }
        )

    return result