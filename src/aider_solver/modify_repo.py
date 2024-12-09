import argparse

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model


def modify_repo_with_aider(model_name: str, instance_background: str) -> None:
    io = InputOutput(yes=True)
    model = Model(model_name)
    coder = Coder.create(main_model=model, io=io)
    coder.run(instance_background)

    # test_cmd = "pytest -v"
    # coder.run(f"/test {test_cmd}")


def main():
    parser = argparse.ArgumentParser(description="Modify a repository with Aider.")
    parser.add_argument(
        "--model-name", type=str, required=True, help="The name of the model to use."
    )
    parser.add_argument(
        "--instance-background",
        type=str,
        required=True,
        help="The instance background information.",
    )

    args = parser.parse_args()

    modify_repo_with_aider(args.model_name, args.instance_background)


if __name__ == "__main__":
    main()
