from __future__ import annotations

from shared.services.answer_key_service import normalize_number


class ScoringError(ValueError):
    pass


def score_y1(key_payload: dict, answer_payload: dict) -> tuple[int, list[int]]:
    key = key_payload.get("answers", "")
    ans = answer_payload.get("answers", "")
    wrong = []
    score = 0
    for idx, (k, a) in enumerate(zip(key, ans), start=1):
        if k == a:
            score += 1
        else:
            wrong.append(idx)
    return score, wrong


def score_y2(key_payload: dict, answer_payload: dict) -> tuple[int, list[int]]:
    key_answers = key_payload.get("answers", {})
    ans_answers = answer_payload.get("answers", {})
    wrong = []
    score = 0
    for item_no, correct in key_answers.items():
        if ans_answers.get(str(item_no)) == correct:
            score += 1
        else:
            wrong.append(int(item_no))
    return score, wrong


def score_open(key_payload: dict, answer_payload: dict) -> tuple[int, list[int]]:
    key_items = key_payload.get("items", [])
    ans_items = answer_payload.get("items", [])
    ans_map = {item.get("item_no"): item for item in ans_items}
    wrong = []
    score = 0
    subparts = key_payload.get("subparts", False)
    for item in key_items:
        item_no = item.get("item_no")
        answer = ans_map.get(item_no)
        if not answer:
            wrong.append(item_no)
            continue
        if subparts:
            correct = True
            for part in ("a", "b"):
                if normalize_number(str(answer.get(part, ""))) != normalize_number(
                    str(item.get(part, ""))
                ):
                    correct = False
                    break
            if correct:
                score += 1
            else:
                wrong.append(item_no)
        else:
            if normalize_number(str(answer.get("answer", ""))) == normalize_number(
                str(item.get("answer", ""))
            ):
                score += 1
            else:
                wrong.append(item_no)
    return score, wrong


def compute_scores(keys: dict, answers: dict) -> dict:
    y1_score, y1_wrong = score_y1(keys["Y1"], answers["Y1"])
    y2_score, y2_wrong = score_y2(keys["Y2"], answers["Y2"])
    o_score, o_wrong = score_open(keys["O"], answers["O"])

    total = y1_score + y2_score + o_score
    return {
        "score_total": total,
        "score_y1": y1_score,
        "score_y2": y2_score,
        "score_o": o_score,
        "incorrect_items": {"Y1": y1_wrong, "Y2": y2_wrong, "O": o_wrong},
    }
