from kubernetes import client
from datetime import datetime, timezone

from cluster.client import apps_v1
from config.settings import DEFAULT_NAMESPACE

from cluster.client import apps_v1
from config.settings import DEFAULT_NAMESPACE
def restart_deployment(
    deployment_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    restarted_at = datetime.now(timezone.utc).isoformat()

    apps_v1.patch_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
        body={
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": restarted_at
                        }
                    }
                }
            }
        },
    )

    return (
        f"Restart started for deployment '{deployment_name}' "
        f"in namespace '{namespace}'."
    )

def update_deployment_image(
    deployment_name: str,
    image: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    deployment = apps_v1.read_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
    )

    containers = deployment.spec.template.spec.containers

    if not containers:
        return f"Deployment '{deployment_name}' has no containers."

    container_name = containers[0].name

    patch_body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": container_name,
                            "image": image,
                        }
                    ]
                }
            }
        }
    }

    apps_v1.patch_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
        body=patch_body,
    )

    return (
        f"Updated container '{container_name}' in deployment "
        f"'{deployment_name}' to image '{image}'."
    )

def get_deployment_status(
    deployment_name: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> dict:
    deployment = apps_v1.read_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
    )

    return {
        "name": deployment.metadata.name,
        "desired_replicas": deployment.spec.replicas or 0,
        "ready_replicas": deployment.status.ready_replicas or 0,
        "available_replicas": deployment.status.available_replicas or 0,
        "updated_replicas": deployment.status.updated_replicas or 0,
    }