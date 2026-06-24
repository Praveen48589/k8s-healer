from config.settings import DEFAULT_NAMESPACE
from tools.event_tools import get_pod_events
from tools.log_tools import get_pod_logs
from tools.pod_tools import list_pods


def troubleshoot_pod(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> dict:
    pods = list_pods(namespace)

    selected_pod = next(
        (pod for pod in pods if pod["name"] == pod_name),
        None,
    )

    if selected_pod is None:
        return {
            "error": (
                f"Pod '{pod_name}' was not found "
                f"in namespace '{namespace}'."
            )
        }

    events = get_pod_events(pod_name, namespace)

    try:
        logs = get_pod_logs(pod_name, namespace)
    except Exception as error:
        logs = f"Could not read logs: {error}"

    return {
        "pod": selected_pod,
        "events": events,
        "logs": logs,
    }