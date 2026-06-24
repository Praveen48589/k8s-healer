from agent.agent import build_agent


def main():
    agent = build_agent()

    print("Kubernetes AI Agent started")
    print("Namespace: agent")
    print("Model: qwen2.5:1.5b")
    print("Type exit to quit")

    while True:
        query = input("\nAsk > ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Stopped.")
            break

        if not query:
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

            print("\nAgent:")
            print(result["messages"][-1].content)

        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()