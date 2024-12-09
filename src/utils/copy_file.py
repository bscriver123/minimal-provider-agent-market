import os
import shutil
from pathlib import Path
from typing import Union

from loguru import logger


def copy_file_to_directory(file_path: Union[Path, str], target_directory: Union[Path, str]) -> None:
    if not os.path.isfile(file_path):
        raise ValueError(f"The file {file_path} does not exist.")

    if not os.path.isdir(target_directory):
        raise ValueError(f"The directory {target_directory} does not exist.")

    shutil.copy(file_path, target_directory)
    logger.info(f"File {file_path} copied to {target_directory}")
