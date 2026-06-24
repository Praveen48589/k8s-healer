from agent.agent import build_agent
from config.settings import DEFAULT_NAMESPACE
from tools.remediation_tools import (
    get_deployment_status,
    update_deployment_image,
)

pending_image_update = None


def print_agent_response(result):
    print("\nAgent:")
    print(result["messages"][-1].content)


def parse_fix_request(text: str):
    prefix = "fix deployment "
    marker = " by changing its image to "

    lower = text.lower()

    if not lower.startswith(prefix):
        return None

    if marker not in lower:
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


def main():
    global pending_image_update

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
            if pending_image_update is None:
                print("\nNo pending change to confirm.")
                continue

            change = pending_image_update

            try:
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

            except Exception as error:
                print(f"\nFailed to apply change: {error}")

            continue

        proposed_change = parse_fix_request(query)

        if proposed_change:
            pending_image_update = proposed_change

            print("\nProposed change:")
            print(f"Deployment: {proposed_change['deployment_name']}")
            print(f"Namespace: {proposed_change['namespace']}")
            print(f"New image: {proposed_change['image']}")
            print("\nNo change has been made.")
            print("Type exactly CONFIRM to apply this change.")
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