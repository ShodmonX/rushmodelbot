from __future__ import annotations

import re
from math import gcd

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.test_answer_key import TestAnswerKey


Y1_PATTERN = re.compile(r"^[ABCD]+$")
MAPPING_PATTERN = re.compile(r"^(\d+)[=-]([A-Z])$")
NUMBER_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?$")
FRACTION_PATTERN = re.compile(r"^-?\d+\s*/\s*\d+$")
OPEN_AB_PATTERN = re.compile(r"(\d{2})\s*([abAB])\s*[:=]\s*([^\s,;]+)")


class ValidationError(ValueError):
    pass


def validate_y1(answers: str, expected_len: int = 32) -> str:
    trimmed = answers.strip().upper()
    if len(trimmed) != expected_len:
        raise ValidationError(f"{expected_len} ta harf bo‘lishi kerak")
    if not Y1_PATTERN.match(trimmed):
        raise ValidationError("Faqat A/B/C/D harflari bo‘lishi kerak")
    return trimmed


def parse_y1_input(raw: str, expected_len: int = 32) -> str:
    cleaned = raw.replace("\n", " ").replace(";", ",").strip().upper()
    if not cleaned:
        raise ValidationError("Bo‘sh javob")
    compact = re.sub(r"[^A-Z]", "", cleaned)
    if len(compact) == expected_len:
        return validate_y1(compact, expected_len=expected_len)

    tokens = re.split(r"[\s,]+", cleaned)
    tokens = [token for token in tokens if token]
    mapping: dict[str, str] = {}
    for token in tokens:
        match = MAPPING_PATTERN.match(token)
        if not match:
            raise ValidationError("Format mos kelmadi")
        num, letter = match.groups()
        mapping[num] = letter

    expected = {str(idx) for idx in range(1, expected_len + 1)}
    missing = expected - set(mapping.keys())
    extra = set(mapping.keys()) - expected
    if missing:
        raise ValidationError(f"Yetishmayapti: {', '.join(sorted(missing)[:5])}...")
    if extra:
        raise ValidationError(f"Ortiqcha: {', '.join(sorted(extra))}")

    ordered = [mapping[str(idx)] for idx in range(1, expected_len + 1)]
    return validate_y1("".join(ordered), expected_len=expected_len)


def parse_y2_choices(raw: str, item_numbers: list[int]) -> dict[str, str]:
    cleaned = raw.replace("\n", " ").replace(";", ",").strip().upper()
    if not cleaned:
        raise ValidationError("Bo‘sh javob")

    allowed = {"A", "B", "C", "D", "E"}
    compact = re.sub(r"[^A-Z]", "", cleaned)
    if len(compact) == len(item_numbers):
        if any(ch not in allowed for ch in compact):
            raise ValidationError("Faqat A, B, C, D, E harflari bo‘lishi kerak")
        return {str(num): compact[idx] for idx, num in enumerate(item_numbers)}

    tokens = re.split(r"[\\s,]+", cleaned)
    tokens = [token for token in tokens if token]
    mapping: dict[str, str] = {}
    for token in tokens:
        match = MAPPING_PATTERN.match(token)
        if not match:
            raise ValidationError("Format mos kelmadi")
        num, letter = match.groups()
        if letter not in allowed:
            raise ValidationError("Faqat A, B, C, D, E harflari bo‘lishi kerak")
        mapping[num] = letter

    expected = {str(num) for num in item_numbers}
    missing = expected - set(mapping.keys())
    extra = set(mapping.keys()) - expected
    if missing:
        raise ValidationError(f"Yetishmayapti: {', '.join(sorted(missing))}")
    if extra:
        raise ValidationError(f"Ortiqcha: {', '.join(sorted(extra))}")
    return mapping


def normalize_number(value: str) -> str:
    cleaned = value.strip().replace(" ", "")
    if NUMBER_PATTERN.match(cleaned):
        if "." in cleaned:
            cleaned = cleaned.rstrip("0").rstrip(".")
            return cleaned or "0"
        return cleaned
    if FRACTION_PATTERN.match(cleaned):
        num_str, den_str = cleaned.split("/")
        num = int(num_str)
        den = int(den_str)
        if den == 0:
            raise ValidationError("Zero denominator")
        sign = -1 if num * den < 0 else 1
        num = abs(num)
        den = abs(den)
        divisor = gcd(num, den)
        num //= divisor
        den //= divisor
        if sign < 0:
            num = -num
        return f"{num}/{den}"
    raise ValidationError("Invalid number format")


def parse_open_ab_bulk(raw: str, item_numbers: list[int]) -> dict[int, dict[str, str]]:
    tokens = OPEN_AB_PATTERN.findall(raw)
    if not tokens:
        raise ValidationError("Format mos kelmadi")

    item_set = {int(num) for num in item_numbers}
    parsed: dict[int, dict[str, str]] = {}
    for num_str, part, value in tokens:
        item_no = int(num_str)
        if item_no not in item_set:
            raise ValidationError(f"Raqam noto‘g‘ri: {item_no}")
        norm = normalize_number(value)
        entry = parsed.get(item_no, {})
        entry[part.lower()] = norm
        parsed[item_no] = entry

    missing_parts: list[str] = []
    for item_no in item_numbers:
        entry = parsed.get(item_no, {})
        for part in ("a", "b"):
            if part not in entry:
                missing_parts.append(f"{item_no}{part}")
    if missing_parts:
        raise ValidationError(f"Yetishmayapti: {', '.join(missing_parts[:8])}")

    return parsed


async def save_section_key(
    session: AsyncSession, test_id: int, section_code: str, payload: dict
) -> TestAnswerKey:
    result = await session.execute(
        select(TestAnswerKey).where(
            TestAnswerKey.test_id == test_id,
            TestAnswerKey.section_code == section_code,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = TestAnswerKey(
            test_id=test_id,
            section_code=section_code,
            payload_json=payload,
        )
        session.add(record)
    else:
        record.payload_json = payload
        session.add(record)
    await session.commit()
    await session.refresh(record)
    return record
