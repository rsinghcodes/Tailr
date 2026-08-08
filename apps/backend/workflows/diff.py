"""Diff between the canonical resume and the rewritten resume.

Emits only the content that actually changed: the summary (when rewritten)
and, per experience entry, the individual bullets that were modified, added,
or removed. Matching is by company + role (the rewrite must preserve them),
so the diff stays readable even when the LLM reorders sections.
"""

import difflib
from typing import Any


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _norm(text: Any) -> str:
    return " ".join(str(text or "").lower().split())


def _bullet_text(bullet: Any) -> str:
    if isinstance(bullet, dict):
        return str(bullet.get("text") or "")
    return str(bullet or "")


def _experience_key(exp: dict[str, Any]) -> str:
    company = str(exp.get("company") or "").strip().lower()
    role = str(exp.get("role") or "").strip().lower()
    return f"{company}|{role}"


def _match_canonical(
    rewritten: list[dict[str, Any]],
    canonical: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any] | None]]:
    """Pair each rewritten experience with its canonical counterpart.

    Primary match is on company + role; unmatched rewritten entries fall back
    to the next unused canonical entry in order (index alignment).
    """
    remaining = list(canonical)
    pairs: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    for exp in rewritten:
        key = _experience_key(exp)
        original: dict[str, Any] | None = None
        for idx, cand in enumerate(remaining):
            if _experience_key(cand) == key:
                original = cand
                remaining.pop(idx)
                break
        if original is None and remaining:
            original = remaining.pop(0)
        pairs.append((exp, original))
    return pairs


def _bullet_changes(
    old_bullets: list[str], new_bullets: list[str]
) -> list[dict[str, Any]]:
    old_norm = [_norm(b) for b in old_bullets]
    new_norm = [_norm(b) for b in new_bullets]
    changes: list[dict[str, Any]] = []

    matcher = difflib.SequenceMatcher(None, old_norm, new_norm, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            paired = min(i2 - i1, j2 - j1)
            for k in range(paired):
                changes.append(
                    {
                        "change_type": "modified",
                        "original": old_bullets[i1 + k],
                        "updated": new_bullets[j1 + k],
                    }
                )
            for i in range(i1 + paired, i2):
                changes.append(
                    {
                        "change_type": "removed",
                        "original": old_bullets[i],
                        "updated": None,
                    }
                )
            for j in range(j1 + paired, j2):
                changes.append(
                    {
                        "change_type": "added",
                        "original": None,
                        "updated": new_bullets[j],
                    }
                )
        elif tag == "delete":
            for i in range(i1, i2):
                changes.append(
                    {
                        "change_type": "removed",
                        "original": old_bullets[i],
                        "updated": None,
                    }
                )
        elif tag == "insert":
            for j in range(j1, j2):
                changes.append(
                    {
                        "change_type": "added",
                        "original": None,
                        "updated": new_bullets[j],
                    }
                )

    return changes


def compute_bullet_diff(
    canonical: dict[str, Any], rewritten: dict[str, Any]
) -> dict[str, Any]:
    """Compare canonical vs rewritten resumes and return only the changes.

    Returns:
        {
          "summary": {"original": str, "updated": str} | None,
          "experience": [
            {
              "company": str | None,
              "role": str | None,
              "bullets": [
                {"change_type": "modified" | "added" | "removed",
                 "original": str | None, "updated": str | None}
              ],
            },
            ...
          ],
        }
    """
    summary_original = str(canonical.get("summary") or "").strip()
    summary_updated = str(rewritten.get("summary") or "").strip()
    summary_change = None
    if (
        summary_original
        and summary_updated
        and _norm(summary_original) != _norm(summary_updated)
    ):
        summary_change = {
            "original": summary_original,
            "updated": summary_updated,
        }

    rewritten_experience = [
        e for e in _as_list(rewritten.get("experience")) if isinstance(e, dict)
    ]
    canonical_experience = [
        e for e in _as_list(canonical.get("experience")) if isinstance(e, dict)
    ]

    experience_changes: list[dict[str, Any]] = []
    for exp, original in _match_canonical(rewritten_experience, canonical_experience):
        new_bullets = [_bullet_text(b) for b in _as_list(exp.get("bullets"))]
        old_bullets = (
            [_bullet_text(b) for b in _as_list(original.get("bullets"))]
            if original is not None
            else []
        )
        bullets = _bullet_changes(old_bullets, new_bullets)
        if bullets:
            experience_changes.append(
                {
                    "company": exp.get("company"),
                    "role": exp.get("role"),
                    "bullets": bullets,
                }
            )

    return {
        "summary": summary_change,
        "experience": experience_changes,
    }
