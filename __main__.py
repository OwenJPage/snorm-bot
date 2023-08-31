import logging
import re
from asyncio import run
from os import getenv
from typing import Tuple

import nest_asyncio
from dotenv import load_dotenv

from lib import main
from lib.structures.logger import SnormLogger


def check_env(name: str) -> Tuple[str, str]:
    """
    Checks if the environment variable is set and returns it

    :param name: Name of the environment variable
    """

    env = getenv(name)

    if env is None:
        raise KeyError(f"Missing environment variable '{name}'")
    else:
        return name.lower(), env


if __name__ == "__main__":
    nest_asyncio.apply()

    logging.setLoggerClass(SnormLogger)

    logger = logging.getLogger("bootstrapper")
    logger.propagate = True

    logger.info("Bootstrapping environment")

    # Load environment variables from .env file
    load_dotenv()

    # Load required keys from required_envs
    env_keys = filter(
        lambda s: s != "",
        re.sub(re.compile(r"\s+"), "", open(".required_envs", "r").read()).split(","),
    )

    # Map env keys to values, raising exception if not found
    envs = dict(map(check_env, env_keys))

    logger.info("Starting main")
    run(main(**envs))
