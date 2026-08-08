from workflows.diff import compute_bullet_diff


def _resume(summary="Original summary", experience=None):
    return {
        "summary": summary,
        "experience": experience or [],
    }


def test_unchanged_resume_produces_no_changes():
    canonical = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": ["Do things"]}])
    rewritten = _resume(summary="Original summary", experience=[{"company": "Acme", "role": "Engineer", "bullets": ["Do things"]}])
    diff = compute_bullet_diff(canonical, rewritten)
    assert diff["summary"] is None
    assert diff["experience"] == []


def test_modified_bullet_is_reported():
    canonical = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": [{"text": "Built a thing"}]}])
    rewritten = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": [{"text": "Built a thing used by 100k users"}]}])
    diff = compute_bullet_diff(canonical, rewritten)
    assert diff["summary"] is None
    assert diff["experience"][0]["bullets"] == [
        {
            "change_type": "modified",
            "original": "Built a thing",
            "updated": "Built a thing used by 100k users",
        }
    ]


def test_added_and_removed_bullets():
    canonical = _resume(
        experience=[
            {
                "company": "Acme",
                "role": "Engineer",
                "bullets": ["Keep this", "Old bullet to drop"],
            }
        ]
    )
    rewritten = _resume(
        experience=[
            {
                "company": "Acme",
                "role": "Engineer",
                "bullets": ["Keep this", "Brand new bullet", "Another new"],
            }
        ]
    )
    diff = compute_bullet_diff(canonical, rewritten)
    bullets = diff["experience"][0]["bullets"]
    assert [(c["change_type"], c["original"], c["updated"]) for c in bullets] == [
        ("modified", "Old bullet to drop", "Brand new bullet"),
        ("added", None, "Another new"),
    ]


def test_removed_tail_bullet():
    canonical = _resume(
        experience=[
            {
                "company": "Acme",
                "role": "Engineer",
                "bullets": ["Keep this", "A", "B"],
            }
        ]
    )
    rewritten = _resume(
        experience=[
            {
                "company": "Acme",
                "role": "Engineer",
                "bullets": ["Keep this", "C"],
            }
        ]
    )
    diff = compute_bullet_diff(canonical, rewritten)
    bullets = diff["experience"][0]["bullets"]
    assert [(c["change_type"], c["original"], c["updated"]) for c in bullets] == [
        ("modified", "A", "C"),
        ("removed", "B", None),
    ]


def test_summary_change_is_reported():
    diff = compute_bullet_diff(
        _resume(summary="I did stuff"),
        _resume(summary="I did stuff with measurable impact"),
    )
    assert diff["summary"] == {
        "original": "I did stuff",
        "updated": "I did stuff with measurable impact",
    }


def test_experience_matched_by_company_and_role_when_reordered():
    canonical = _resume(
        experience=[
            {"company": "Acme", "role": "Engineer", "bullets": ["Acme bullet"]},
            {"company": "Globex", "role": "Manager", "bullets": ["Globex bullet"]},
        ]
    )
    rewritten = _resume(
        experience=[
            {"company": "Globex", "role": "Manager", "bullets": ["Globex bullet improved"]},
            {"company": "Acme", "role": "Engineer", "bullets": ["Acme bullet"]},
        ]
    )
    diff = compute_bullet_diff(canonical, rewritten)
    assert len(diff["experience"]) == 1
    assert diff["experience"][0]["company"] == "Globex"
    assert diff["experience"][0]["role"] == "Manager"


def test_whitespace_only_change_is_ignored():
    canonical = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": ["Do  things"]}])
    rewritten = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": ["do things"]}])
    diff = compute_bullet_diff(canonical, rewritten)
    assert diff["experience"] == []


def test_string_and_dict_bullets_are_both_supported():
    canonical = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": ["Plain string"]}])
    rewritten = _resume(experience=[{"company": "Acme", "role": "Engineer", "bullets": [{"text": "Plain string expanded"}]}])
    diff = compute_bullet_diff(canonical, rewritten)
    assert diff["experience"][0]["bullets"][0]["original"] == "Plain string"
    assert diff["experience"][0]["bullets"][0]["updated"] == "Plain string expanded"
