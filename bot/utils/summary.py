from __future__ import annotations


def format_y1_block(y1_answers: dict | None, expected_len: int) -> tuple[str, bool]:
    if not y1_answers or "answers" not in y1_answers:
        return "-", False
    answers = y1_answers.get("answers", "")
    if len(answers) != expected_len:
        return "-", False
    items = [f"{idx}:{letter}" for idx, letter in enumerate(answers, start=1)]
    lines = ["  ".join(items[i : i + 8]) for i in range(0, len(items), 8)]
    return "\n".join(lines), True


def format_y2_block(y2_answers: dict | None, item_numbers: list[int]) -> tuple[str, bool]:
    if not y2_answers or "answers" not in y2_answers:
        return "-", False
    mapping = y2_answers.get("answers", {})
    if not isinstance(mapping, dict):
        return "-", False
    parts = []
    for item_no in item_numbers:
        value = mapping.get(str(item_no))
        if not value:
            return "-", False
        parts.append(f"{item_no}:{value}")
    return "  ".join(parts), True


def format_open_block(
    open_items: dict | None, item_numbers: list[int]
) -> tuple[str, bool]:
    if not open_items:
        return "-", False
    lines = []
    complete = True
    for item_no in item_numbers:
        entry = open_items.get(str(item_no), {})
        a_val = entry.get("a", "...")
        b_val = entry.get("b", "...")
        if "a" not in entry or "b" not in entry:
            complete = False
        lines.append(f"{item_no}a={a_val} | {item_no}b={b_val}")
    return "\n".join(lines), complete


def _compute_progress(data: dict) -> tuple[bool, bool, bool]:
    template = data.get("template_structure", {})
    y1_section = next((s for s in template.get("sections", []) if s["code"] == "Y1"), {})
    y2_section = next((s for s in template.get("sections", []) if s["code"] == "Y2"), {})
    o_section = next((s for s in template.get("sections", []) if s["code"] == "O"), {})
    y1_block, y1_ok = format_y1_block(
        data.get("y1_answers"), y1_section.get("item_count", 32)
    )
    y2_block, y2_ok = format_y2_block(
        data.get("y2_answers"), y2_section.get("item_numbers", [33, 34, 35])
    )
    open_block, open_ok = format_open_block(
        data.get("open_items"), o_section.get("item_numbers", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45])
    )
    return y1_ok, y2_ok, open_ok


def build_teacher_summary(
    data: dict,
    instruction: str | None = None,
    error: str | None = None,
) -> str:
    template = data.get("template_structure", {})
    y1_section = next((s for s in template.get("sections", []) if s["code"] == "Y1"), {})
    y2_section = next((s for s in template.get("sections", []) if s["code"] == "Y2"), {})
    o_section = next((s for s in template.get("sections", []) if s["code"] == "O"), {})
    y1_block, y1_ok = format_y1_block(
        data.get("y1_answers"), y1_section.get("item_count", 32)
    )
    y2_block, y2_ok = format_y2_block(
        data.get("y2_answers"), y2_section.get("item_numbers", [33, 34, 35])
    )
    open_block, open_ok = format_open_block(
        data.get("open_items"), o_section.get("item_numbers", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45])
    )
    step1 = "✅" if y1_ok else "❌"
    step2 = "✅" if y2_ok else "❌"
    step3 = "✅" if open_ok else "❌"
    lines = [
        "Test javoblari (O'qituvchi)",
        f"Test: {data.get('test_title', '-')}",
        "",
        f"1-qadam: 1-32 savollar (A-D variantli) -> {step1}",
        f"2-qadam: 33-35 savollar (A-E variantli) -> {step2}",
        f"3-qadam: 36-45 savollar (a va b) -> {step3}",
        "",
        "Kiritilgan javoblar:",
        "1-32 savollar:",
        y1_block,
        "",
        "33-35 savollar:",
        y2_block,
        "",
        "36-45 savollar:",
        open_block,
    ]
    if error:
        lines.append(f"Xato: {error}")
    if instruction:
        lines.append(f"Ko'rsatma: {instruction}")
    lines.append("Amallar: pastdagi tugmalar.")
    return "\n".join(lines)


def build_student_summary(
    data: dict,
    instruction: str | None = None,
    error: str | None = None,
) -> str:
    template = data.get("template_structure", {})
    y1_section = next((s for s in template.get("sections", []) if s["code"] == "Y1"), {})
    y2_section = next((s for s in template.get("sections", []) if s["code"] == "Y2"), {})
    o_section = next((s for s in template.get("sections", []) if s["code"] == "O"), {})
    y1_block, y1_ok = format_y1_block(
        data.get("y1_answers"), y1_section.get("item_count", 32)
    )
    y2_block, y2_ok = format_y2_block(
        data.get("y2_answers"), y2_section.get("item_numbers", [33, 34, 35])
    )
    open_block, open_ok = format_open_block(
        data.get("open_items"), o_section.get("item_numbers", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45])
    )
    step1 = "✅" if y1_ok else "❌"
    step2 = "✅" if y2_ok else "❌"
    step3 = "✅" if open_ok else "❌"
    lines = [
        "Test yechilyapti (O'quvchi)",
        f"Test kodi: `{data.get('access_code', '-')}`",
        "",
        f"1-qadam: 1-32 savollar (A-D variantli) -> {step1}",
        f"2-qadam: 33-35 savollar (A-E variantli) -> {step2}",
        f"3-qadam: 36-45 savollar (a va b) -> {step3}",
        "",
        "Kiritilgan javoblar:",
        "1-32 savollar:",
        y1_block,
        "",
        "33-35 savollar:",
        y2_block,
        "",
        "36-45 savollar:",
        open_block,
    ]
    if error:
        lines.append(f"Xato: {error}")
    if instruction:
        lines.append(f"Ko'rsatma: {instruction}")
    lines.append("Amallar: pastdagi tugmalar.")
    return "\n".join(lines)


def teacher_progress_stage(data: dict) -> int:
    y1_ok, y2_ok, open_ok = _compute_progress(data)
    if not y1_ok:
        return 0
    if not y2_ok:
        return 1
    if not open_ok:
        return 2
    return 3


def student_progress_stage(data: dict) -> int:
    return teacher_progress_stage(data)
