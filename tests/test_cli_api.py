import json

from fastapi.testclient import TestClient

from resume_screener.api import app
from resume_screener.cli import main


def test_cli_json(samples, tmp_path, capsys):
    out = tmp_path / "out.json"
    code = main(["--job", str(samples / "job_description.txt"), "--resumes", str(samples / "resumes"),
                 "--format", "json", "--output", str(out)])
    assert code == 0
    data = json.loads(out.read_text())
    assert len(data) == 4 and data[0]["name"] == "amina_bello.txt"


def test_cli_table_top(samples, capsys):
    assert main(["--job", str(samples / "job_description.txt"), "--resumes", str(samples / "resumes"), "--top", "2"]) == 0
    out = capsys.readouterr().out
    assert "amina_bello.txt" in out and "ngozi_eze.txt" not in out


def test_cli_csv(samples, capsys):
    main(["--job", str(samples / "job_description.txt"), "--resumes", str(samples / "resumes"), "--format", "csv"])
    assert capsys.readouterr().out.startswith("rank,name,score")


def test_cli_bad_folder(tmp_path, samples):
    assert main(["--job", str(samples / "job_description.txt"), "--resumes", str(tmp_path / "nope")]) == 2


client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_screen_endpoint(samples, job_text):
    files = [
        ("resumes", ("amina.txt", (samples / "resumes" / "amina_bello.txt").read_bytes(), "text/plain")),
        ("resumes", ("tunde.pdf", (samples / "resumes" / "tunde_adebayo.pdf").read_bytes(), "application/pdf")),
        ("resumes", ("ngozi.txt", (samples / "resumes" / "ngozi_eze.txt").read_bytes(), "text/plain")),
    ]
    resp = client.post("/screen", data={"job_description": job_text}, files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 3
    assert body["results"][-1]["name"] == "ngozi.txt"


def test_screen_rejects_bad_type(job_text):
    resp = client.post("/screen", data={"job_description": job_text}, files=[("resumes", ("x.exe", b"MZ", "application/octet-stream"))])
    assert resp.status_code == 415
