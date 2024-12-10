import os

from docker import from_env as docker_from_env
from dotenv import load_dotenv
from loguru import logger

DOCKER_IMAGE = "paulgauthier/aider"
load_dotenv()
ENV_VARS = {key: os.getenv(key) for key in os.environ.keys()}


def launch_container_with_repo_mounted(
    repo_directory: str, model_name: str, instance_background: str
) -> None:
    docker_client = docker_from_env()
    entrypoint = (
        "/bin/bash -c 'source /venv/bin/activate && "
        "python modify_repo.py "
        f'--model-name "{model_name}" '
        f'--instance-background "{instance_background}"'
        "'"
    )
    logger.info(f"Launching container with entrypoint: {entrypoint}")
    container = docker_client.containers.run(
        DOCKER_IMAGE,
        entrypoint=entrypoint,
        user=f"{os.getuid()}:{os.getgid()}",
        volumes={
            f"{repo_directory}/.": {"bind": "/app", "mode": "rw"},
            "/tmp/aider_cache": {"bind": "/home/ubuntu", "mode": "rw"},
        },
        environment=ENV_VARS,
        detach=True,
        tty=True,
        stdin_open=True,
    )
    logger.info("Container launched. Waiting for it to finish...")

    result = container.wait()

    exit_status = result.get("StatusCode", -1)
    logger.info(f"Container finished with exit code: {exit_status}")

    logs = container.logs().decode("utf-8")
    logger.info(f"Container logs:\n{logs}")

    container.remove()
    logger.info("Container removed")


if __name__ == "__main__":
    launch_container_with_repo_mounted(
        os.getcwd(),
        "gpt-4o",
        (
            "change readme to take into account how docker uses volumes. Confirm in the readme if "
            "we are using any volume mount. If yes, provide explicit references"
        ),
    )
