from cluster.client import core_v1
from config.settings import DEFAULT_NAMESPACE


def get_pod_events(
    pod_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> list[dict]:
    events = core_v1.list_namespaced_event(
        namespace=namespace,
        field_selector=f"involvedObject.name={pod_name}",
    )

    return [
        {
            "type": event.type,
            "reason": event.reason,
            "message": event.message,
            "count": event.count,
        }
        for event in events.items
    ]