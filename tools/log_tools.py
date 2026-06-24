from cluster.client import core_v1
from config.settings import DEFAULT_NAMESPACE


def get_pod_logs(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    return core_v1.read_namespaced_pod_log(
        name=pod_name,
        namespace=namespace,
        tail_lines=100,
    )


def get_previous_pod_logs(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    return core_v1.read_namespaced_pod_log(
        name=pod_name,
        namespace=namespace,
        previous=True,
        tail_lines=100,
    )