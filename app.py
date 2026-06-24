from agent.agent import build_agent
from config.settings import DEFAULT_NAMESPACE
from tools.deployment_tools import scale_deployment
from tools.remediation_tools import (
    get_deployment_status,
    update_deployment_image,
)

pending_image_update = None
pending_scale = None


def print_agent_response(result):
    print("\nAgent:")
    print(result["messages"][-1].content)


def parse_fix_request(text: str):
    prefix = "fix deployment "
    marker = " by changing its image to "

    lower = text.lower()

    if not lower.startswith(prefix) or marker not in lower:
        return None

    marker_index = lower.index(marker)

    deployment_name = text[len(prefix):marker_index].strip()
    image = text[marker_index + len(marker):].strip()

    if not deployment_name or not image:
        return None

    return {
        "deployment_name": deployment_name,
        "image": image,
        "namespace": DEFAULT_NAMESPACE,
    }


def parse_scale_request(text: str):
    """
    Supports:
    Scale deployment test-nginx to 3 replicas
    """
    parts = text.strip().split()

    if len(parts) != 6:
        return None

    if parts[0].lower() != "scale":
        return None

    if parts[1].lower() != "deployment":
        return None

    if parts[3].lower() != "to":
        return None

    if parts[5].lower() not in {"replica", "replicas"}:
        return None

    deployment_name = parts[2]

    try:
        replicas = int(parts[4])
    except ValueError:
        return None

    if replicas < 0:
        return None

    return {
        "deployment_name": deployment_name,
        "replicas": replicas,
        "namespace": DEFAULT_NAMESPACE,
    }


def main():
    global pending_image_update, pending_scale

    agent = build_agent()

    print("Kubernetes AI Agent started")
    print(f"Namespace: {DEFAULT_NAMESPACE}")
    print("Model: qwen2.5:1.5b")
    print("Type exit to quit")

    while True:
        query = input("\nAsk > ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Stopped.")
            break

        if not query:
            continue

        if query.upper() == "CONFIRM":
            try:
                if pending_image_update is not None:
                    change = pending_image_update

                    message = update_deployment_image(
                        deployment_name=change["deployment_name"],
                        image=change["image"],
                        namespace=change["namespace"],
                    )

                    print(f"\nApplied: {message}")

                    status = get_deployment_status(
                        deployment_name=change["deployment_name"],
                        namespace=change["namespace"],
                    )

                    print(f"Verification: {status}")

                    pending_image_update = None
                    continue

                if pending_scale is not None:
                    change = pending_scale

                    message = scale_deployment(
                        deployment_name=change["deployment_name"],
                        replicas=change["replicas"],
                        namespace=change["namespace"],
                    )

                    print(f"\nApplied: {message}")

                    status = get_deployment_status(
                        deployment_name=change["deployment_name"],
                        namespace=change["namespace"],
                    )

                    print(f"Verification: {status}")

                    pending_scale = None
                    continue

                print("\nNo pending change to confirm.")

            except Exception as error:
                print(f"\nFailed to apply change: {error}")

            continue

        scale_change = parse_scale_request(query)

        if scale_change:
            pending_scale = scale_change

            print("\nProposed scale:")
            print(f"Deployment: {scale_change['deployment_name']}")
            print(f"Namespace: {scale_change['namespace']}")
            print(f"Replicas: {scale_change['replicas']}")
            print("\nNo change has been made.")
            print("Type exactly CONFIRM to apply this scale.")
            continue

        proposed_change = parse_fix_request(query)

        if proposed_change:
            pending_image_update = proposed_change

            print("\nProposed image update:")
            print(f"Deployment: {proposed_change['deployment_name']}")
            print(f"Namespace: {proposed_change['namespace']}")
            print(f"New image: {proposed_change['image']}")
            print("\nNo change has been made.")
            print("Type exactly CONFIRM to apply this image update.")
            continue

        try:
            result = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": query,
                        }
                    ]
                }
            )

            print_agent_response(result)

        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()