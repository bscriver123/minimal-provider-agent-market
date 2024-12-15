import argparse

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model


def modify_repo_with_tool(dev_tool, model_name, instance_background, test_command=None) -> None:
    if dev_tool == "aider":
        io = InputOutput(yes=True)
        model = Model(model_name)
        coder = Coder.create(main_model=model, io=io)
        coder.run(instance_background)

        if test_command:
            coder.run(f"/test {test_command}")
    elif dev_tool == "open_hands":
        # Implement the logic for open_hands here
        pass
    else:
        raise ValueError(f"Unsupported development tool: {dev_tool}")


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
    parser.add_argument(
        "--test-command",
        type=str,
        required=False,
        help="An optional test command to run.",
    )

    args = parser.parse_args()

    from src.config import SETTINGS
    modify_repo_with_tool(SETTINGS.dev_tool, args.model_name, args.instance_background, args.test_command)


if __name__ == "__main__":
    main()
