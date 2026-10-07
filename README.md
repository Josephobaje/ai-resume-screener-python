# AI Resume Screener

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E?logo=scikitlearn&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Screen dozens of CVs in seconds. **AI Resume Screener** reads resumes in PDF, TXT or Markdown, compares each one with a job description and ranks the candidates. You can use it from the command line or as a REST API.

Each candidate gets a score from 0 to 100 that combines two things:

1. **Semantic similarity**: TF-IDF vectors (unigrams and bigrams) compared with cosine similarity.
2. **Skill coverage**: the share of required skills found in the resume, using a skills vocabulary with aliases (for example `PostgreSQL` counts as `sql` and `pytest` counts as `testing`).

## Features

- Parses **PDF** (via `pypdf`), **TXT** and **Markdown** resumes
- Detects required skills from the job description automatically, or takes your own list with `--skills`
- Lists **matched and missing skills** for every candidate
- Extracts **email, phone and years of experience**
- Gives a recommendation: *Strong match*, *Possible match* or *Weak match*
- CLI output as a table, **JSON** or **CSV**
- **FastAPI** endpoint for uploading several resumes at once, with file type and size limits
- 19 pytest tests covering the parser, scoring, CLI and API

## Tech stack

Python 3.10+, scikit-learn (TF-IDF, cosine similarity), pypdf, FastAPI, Uvicorn, pytest

## Quick start

```bash
git clone https://github.com/Josephobaje/ai-resume-screener-python.git
cd ai-resume-screener-python
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Command line

```bash
python -m resume_screener --job samples/job_description.txt --resumes samples/resumes
```

```text
 #  Candidate                     Score  Skills  Recommendation
------------------------------------------------------------------------------
 1  amina_bello.txt                77.3    100%  Strong match - shortlist
 2  tunde_adebayo.pdf              44.0     54%  Weak match
    missing: aws, ci/cd, communication, cybersecurity, django, teamwork
 3  chidi_okafor.md                23.9     31%  Weak match
    missing: aws, ci/cd, communication, cybersecurity, django, docker, fastapi, teamwork, testing
 4  ngozi_eze.txt                   6.4      8%  Weak match
    missing: aws, ci/cd, cybersecurity, django, docker, fastapi, git, python, rest api, sql, teamwork, testing
```

More options:

```bash
# Only the top 3, as CSV for Excel
python -m resume_screener --job jd.txt --resumes ./cvs --top 3 --format csv --output shortlist.csv

# Use your own required skills instead of the detected ones
python -m resume_screener --job jd.txt --resumes ./cvs --skills "python,fastapi,docker,sql"
```

### REST API

```bash
uvicorn resume_screener.api:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI, or call it with curl:

```bash
curl -X POST http://127.0.0.1:8000/screen \
  -F "job_description=$(cat samples/job_description.txt)" \
  -F "resumes=@samples/resumes/amina_bello.txt" \
  -F "resumes=@samples/resumes/tunde_adebayo.pdf"
```

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness check |
| `POST` | `/screen` | Form fields `job_description`, `resumes` (one or more files) and optional `required_skills` (comma-separated). Returns ranked results. |

## Running tests

```bash
pytest
```

## Project structure

```text
resume_screener/
  parser.py    # PDF/TXT/MD text extraction
  skills.py    # skills vocabulary and alias matching
  scorer.py    # TF-IDF similarity, skill coverage, contact and experience extraction
  cli.py       # command-line interface
  api.py       # FastAPI app
samples/       # sample job description and four resumes (one PDF)
tests/         # pytest suite
```

## Extending

- Add skills or aliases in `resume_screener/skills.py`.
- Change the balance between similarity and skills by passing `weights={"similarity": 0.5, "skills": 0.5}` to `screen_resumes()`.

> The score is meant to help a recruiter sort resumes, not to replace human judgement. Always review candidates yourself.

## Author

**Joseph Obaje**, Full Stack Developer (PHP, Python, Flutter) and Cybersecurity Specialist

- GitHub: [@Josephobaje](https://github.com/Josephobaje)
- LinkedIn: [joseph-obaje](https://www.linkedin.com/in/joseph-obaje)
- Email: [josephobaje264@gmail.com](mailto:josephobaje264@gmail.com)

## License

Released under the [MIT License](LICENSE). © 2026 Joseph Obaje
