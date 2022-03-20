from dotenv import dotenv_values
from typing import Dict


def read_dotenv(prefix: str) -> Dict[str, str]:
    """
    Return a dict of .env values having a specific <prefix>, stripped from said <prefix>. Beware that all values are
    returned as strings.
    :param prefix: A string
    :return: A dict of .env values. All values are strings.
    """
    offset = len(prefix)
    return {k[offset:]: v for k, v in dotenv_values().items() if k.startswith(prefix)}
