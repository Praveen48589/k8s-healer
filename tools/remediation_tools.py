from kubernetes import client

from cluster.client import apps_v1
from config.settings import DEFAULT_NAMESPACE


def update_deployment_image(
    deployment_name: str,
    image: str,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    patch_body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": deployment_name,
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
        f"Updated deployment '{deployment_name}' "
        f"to image '{image}' in namespace '{namespace}'."
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