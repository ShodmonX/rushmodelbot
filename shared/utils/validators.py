import re

NAME_PATTERN = re.compile(r"^[A-Za-z '\u02BB\u2019]{2,40}$")


def normalize_name(value: str) -> str:
    return " ".join(value.strip().split())


def is_valid_name(value: str) -> bool:
    return bool(NAME_PATTERN.match(value))
