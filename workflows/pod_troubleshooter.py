from config.settings import DEFAULT_NAMESPACE
from tools.event_tools import get_pod_events
from tools.log_tools import get_pod_logs, get_previous_pod_logs
from tools.pod_tools import list_pods


def troubleshoot_pod(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> dict:
    pods = list_pods(namespace)

    pod = next(
        (item for item in pods if item["name"] == pod_name),
        None,
    )

    if pod is None:
        return {
            "error": f"Pod '{pod_name}' was not found in namespace '{namespace}'."
        }

    events = get_pod_events(pod_name, namespace)

    try:
        logs = get_pod_logs(pod_name, namespace)
    except Exception as error:
        logs = f"Could not read current logs: {error}"

    try:
        previous_logs = get_previous_pod_logs(pod_name, namespace)
    except Exception as error:
        previous_logs = f"Could not read previous logs: {error}"

    diagnosis = "No clear failure detected."

    for container in pod["containers"]:
        waiting_reason = container["waiting_reason"]
        exit_code = container["last_exit_code"]
        command = container["command"]
        args = container["args"]

        if waiting_reason == "CrashLoopBackOff":
            diagnosis = (
                f"CrashLoopBackOff detected for container '{container['name']}'. "
                f"The previous container exited with code {exit_code}. "
                f"Configured command: {command} {args}."
            )

        elif waiting_reason in {"ImagePullBackOff", "ErrImagePull"}:
            diagnosis = (
                f"Image pull failure for image '{container['image']}'. "
                f"Reason: {waiting_reason}."
            )

    return {
        "pod": pod,
        "diagnosis": diagnosis,
        "events": events,
        "logs": logs,
        "previous_logs": previous_logs,
    }   