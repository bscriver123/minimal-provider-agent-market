import os

from docker import from_env as docker_from_env
from dotenv import load_dotenv

DOCKER_IMAGE = "paulgauthier/aider"
load_dotenv()
ENV_VARS = {key: os.getenv(key) for key in os.environ.keys()}


def solve_instance_with_aider(repo_directory: str):
    client = docker_from_env()
    # docker run -it --user $(id -u):$(id -g) --volume $(pwd)/.:/app
    # --entrypoint /bin/bash --env-file .env paulgauthier/aider
    docker_client = docker_from_env()
    container = docker_client.containers.run(
        DOCKER_IMAGE,
        "/bin/bash",
        user=f"{os.getuid()}:{os.getgid()}",
        volumes={f"{repo_directory}/.": {"bind": "/app", "mode": "rw"}},
        environment=ENV_VARS,
        detach=True,
        tty=True,
        stdin_open=True,
        # remove=True,
    )


if __name__ == "__main__":
    solve_instance_with_aider(os.getcwd())
