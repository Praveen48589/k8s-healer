from cluster.client import apps_v1
from config.settings import DEFAULT_NAMESPACE


def list_deployments(namespace: str = DEFAULT_NAMESPACE) -> list[dict]:
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)

    return [
        {
            "name": deployment.metadata.name,
            "desired": deployment.spec.replicas or 0,
            "available": deployment.status.available_replicas or 0,
        }
        for deployment in deployments.items
    ]


def scale_deployment(
    deployment_name: str,
    replicas: int,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    apps_v1.patch_namespaced_deployment_scale(
        name=deployment_name,
        namespace=namespace,
        body={"spec": {"replicas": replicas}},
    )

    return f"Scaled {deployment_name} to {replicas} replicas."
