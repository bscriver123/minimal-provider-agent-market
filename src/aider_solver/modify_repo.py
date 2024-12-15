import argparse

from aider.coders import Coder
from loguru import logger
from aider.io import InputOutput
from aider.models import Model


def verify_tests(coder: Coder) -> bool:
    """Verify if tests are present and executed."""
    logger.info("Verifying if tests are present and executed.")
    # Check for the presence of test files
    test_files = coder.run("find . -name 'test_*.py'")
    if not test_files:
        logger.warning("No test files found.")
        return False

    # Run the test command and check the output
    test_results = coder.run("pytest")
    if "failed" in test_results:
        logger.warning("Some tests failed.")
        return False

    logger.info("All tests are verified and executed successfully.")
    return True


def modify_repo_with_aider(model_name, instance_background, test_command=None) -> None:
    io = InputOutput(yes=True)
    model = Model(model_name)
    coder = Coder.create(main_model=model, io=io)
    coder.run(instance_background)

    if not verify_tests(coder):
        logger.error("Verification failed: Tests are not present or executed.")
        return
        coder.run(f"/test {test_command}")


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

    modify_repo_with_aider(args.model_name, args.instance_background, args.test_command)


if __name__ == "__main__":
    main()
