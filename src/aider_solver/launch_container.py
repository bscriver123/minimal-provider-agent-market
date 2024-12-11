import os
import shlex
from docker import from_env as docker_from_env
from dotenv import load_dotenv
from loguru import logger
import re

DOCKER_IMAGE = "paulgauthier/aider"
load_dotenv()
ENV_VARS = {key: os.getenv(key) for key in os.environ.keys()}


def launch_container_with_repo_mounted(
    repo_directory: str, model_name: str, instance_background: str, test_command: str
) -> None:
    docker_client = docker_from_env()
    
    escaped_background = instance_background.replace("'", "'\"'\"'")
    escaped_test_command = shlex.quote(test_command) if test_command else ""
    
    test_args_and_command = f' --test-command {escaped_test_command}' if test_command else ""
    
    entrypoint = [
        "/bin/bash",
        "-c",
        (f"source /venv/bin/activate && python modify_repo.py --model-name {shlex.quote(model_name)} "
        f"--instance-background '{escaped_background}'{test_args_and_command}")
    ]
    
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
    logger.info("Container launched. Streaming logs...")

    for log in container.logs(stream=True, follow=True):
        try:    
            print(log.decode('utf-8'), end='', flush=True)
        except UnicodeDecodeError:
            logger.warning("Failed to decode log: " + str(log))

    logs = container.logs().decode("utf-8")
    anti_escape_logs = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    logs = anti_escape_logs.sub('', logs).split("Tokens:")[0]

    result = container.wait()

    exit_status = result.get("StatusCode", -1)
    logger.info(f"Container finished with exit code: {exit_status}")

    container.remove()
    logger.info("Container removed")

    return logs