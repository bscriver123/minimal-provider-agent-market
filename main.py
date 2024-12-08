import asyncio
import os
import sys
from pathlib import Path

from loguru import logger

from src.market_scan import async_handler as market_scan_async_handler
from src.solve_instances import handler as solve_instances_handler


async def run_tasks():
    try:
        # Market scan task
        logger.info("Starting market scan lambda...")
        await market_scan_async_handler()
        logger.info("Market scan completed successfully")

        # Solve instances task
        logger.info("Starting solve_instances lambda...")
        solve_result = solve_instances_handler(None, None)
        logger.info("Solve instances completed with result: " f"{solve_result}")

    except Exception as e:
        logger.exception("Error during execution: " f"{str(e)}")
        # Don't raise the exception to keep the loop running


async def main():
    logger.info("Starting application...")
    while True:
        await run_tasks()
        logger.info("Waiting 10 seconds before next iteration...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.exception("Fatal error in main loop: " f"{str(e)}")
        sys.exit(1)
