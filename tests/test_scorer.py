import pytest

from resume_screener.skills import find_skills
from resume_screener.scorer import extract_contact, extract_years_experience, recommend, screen_resumes
from resume_screener.cli import load_resumes


def test_find_skills_aliases():
    skills = find_skills("Built APIs with FastAPI, PostgreSQL and Node.js; wrote pytest suites")
    assert {"fastapi", "sql", "node.js", "testing", "rest api"} <= skills


def test_find_skills_word_boundaries():
    # "javascript" must not be found inside unrelated words, and "php" not in "graphql".
    assert "php" not in find_skills("GraphQL graphics")


def test_ranking_order(samples, job_text):
    results = screen_resumes(job_text, load_resumes(samples / "resumes"))
    names = [r.name for r in results]
    assert names[0] == "amina_bello.txt"
    assert names[-1] == "ngozi_eze.txt"
    assert results[0].score > results[-1].score
    assert results[0].recommendation.startswith("Strong")


def test_required_skills_override(job_text):
    results = screen_resumes(job_text, {"a": "I know Flutter and Dart"}, required_skills=["Flutter", "Dart", "Python"])
    r = results[0]
    assert r.matched_skills == ["dart", "flutter"]
    assert r.missing_skills == ["python"]
    assert r.skill_coverage == pytest.approx(2 / 3, abs=1e-3)


def test_contact_and_years():
    text = "Jane Doe jane@example.com +234 803 555 0101. I have 6+ years of backend experience and 2 years experience in Go."
    email, phone = extract_contact(text)
    assert email == "jane@example.com"
    assert phone and "803" in phone
    assert extract_years_experience(text) == 6


def test_recommend_thresholds():
    assert recommend(80) == "Strong match - shortlist"
    assert recommend(50) == "Possible match - review"
    assert recommend(10) == "Weak match"


def test_empty_job_rejected():
    with pytest.raises(ValueError):
        screen_resumes("   ", {"a": "python"})
