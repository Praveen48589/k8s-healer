import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_NAMESPACE = os.getenv("K8S_NAMESPACE", "agent")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")