import re
from typing import Annotated

import nh3
from pydantic import EmailStr, AfterValidator

String = Annotated[str, AfterValidator(lambda v: nh3.clean(v))]
EmailString = Annotated[
    EmailStr, AfterValidator(lambda v: nh3.clean(v).lower().strip())
]

PASSWORD_LENGTH = 8

PASSWORD_REGEX = re.compile(
    rf"""
    ^
    (?=.*[0-9])                # digit
    (?=.*[a-z])                # lowercase
    (?=.*[A-Z])                # uppercase
    (?=.*[#&*$%^(!@)\-+])      # special character
    .{{{PASSWORD_LENGTH},}}    # minimum length
    $
    """,
    re.VERBOSE,
)

SPECIAL_CHARS = set("#&*$%^(!@)-+")


def _strong_password(password: str) -> str:
    value = password

    if PASSWORD_REGEX.match(value):
        return password

    errors: list[str] = []

    if len(value) < PASSWORD_LENGTH:
        errors.append(f"have at least {PASSWORD_LENGTH} characters")
    if not re.search(r"[0-9]", value):
        errors.append("contain digits")
    if not re.search(r"[A-Z]", value):
        errors.append("contain uppercase letters")
    if not re.search(r"[a-z]", value):
        errors.append("contain lowercase letters")
    if not any(c in SPECIAL_CHARS for c in value):
        errors.append("contain special characters")

    raise ValueError(f"must {', '.join(errors)}")


IsStrongPassword = Annotated[String, AfterValidator(_strong_password)]
