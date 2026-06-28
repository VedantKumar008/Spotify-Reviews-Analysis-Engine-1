"""Verify the Groq API key loaded from phase4-backend-api/.env."""

from api.groq_utils import get_groq_api_status


def main() -> None:
    status = get_groq_api_status()
    print(f"Env file: {status['env_file']}")
    print(f"Configured: {status['configured']}")
    print(f"Key hint: {status['key_hint']}")
    print(f"Valid: {status['valid']}")

    if status["error"]:
        print(f"Error: {status['error']}")


if __name__ == "__main__":
    main()
