import sys
import time

from loguru import logger

from src.market_scan import market_scan_handler
from src.solve_instances import solve_instances_handler


def run_tasks():
    try:
        logger.info("Starting market scan lambda...")
        market_scan_handler()
        logger.info("Market scan completed successfully")

        logger.info("Starting solve_instances lambda...")
        solve_instances_handler()
        logger.info("solve_instances completed successfully")

    except Exception as e:
        logger.exception("Error during execution: " f"{str(e)}")
        # Don't raise the exception to keep the loop running


def main():
    logger.info("Starting application...")
    while True:
        run_tasks()
        logger.info("Waiting 10 seconds before next iteration...")
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.exception("Fatal error in main loop: " f"{str(e)}")
        sys.exit(1)
