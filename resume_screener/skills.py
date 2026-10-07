"""A small, extendable skills vocabulary with aliases.

Each canonical skill maps to the regex patterns that count as a mention.
"""

from __future__ import annotations

import re

SKILLS: dict[str, list[str]] = {
    "python": [r"python"],
    "django": [r"django"],
    "fastapi": [r"fast\s?api"],
    "flask": [r"flask"],
    "php": [r"php"],
    "laravel": [r"laravel"],
    "javascript": [r"javascript", r"\bjs\b", r"es6"],
    "typescript": [r"typescript", r"\bts\b"],
    "react": [r"react(?:\.?js)?"],
    "node.js": [r"node(?:\.?js)?", r"express(?:\.?js)?"],
    "flutter": [r"flutter"],
    "dart": [r"\bdart\b"],
    "sql": [r"\bsql\b", r"mysql", r"postgres(?:ql)?", r"sqlite", r"mariadb"],
    "mongodb": [r"mongo(?:db)?"],
    "rest api": [r"rest(?:ful)?\s?api", r"\bapis?\b"],
    "graphql": [r"graphql"],
    "docker": [r"docker"],
    "kubernetes": [r"kubernetes", r"\bk8s\b"],
    "aws": [r"\baws\b", r"amazon web services"],
    "git": [r"\bgit\b", r"github", r"gitlab"],
    "linux": [r"linux", r"ubuntu", r"debian"],
    "machine learning": [r"machine learning", r"\bml\b", r"scikit-learn", r"sklearn"],
    "data analysis": [r"data analysis", r"pandas", r"numpy"],
    "cybersecurity": [r"cyber\s?security", r"penetration test", r"owasp", r"\bsiem\b"],
    "wordpress": [r"wordpress"],
    "seo": [r"\bseo\b", r"search engine optimi[sz]ation"],
    "html": [r"html5?"],
    "css": [r"css3?", r"tailwind", r"bootstrap"],
    "testing": [r"pytest", r"unit test", r"jest", r"phpunit", r"\btdd\b"],
    "ci/cd": [r"ci/cd", r"github actions", r"jenkins", r"gitlab ci"],
    "communication": [r"communication"],
    "teamwork": [r"teamwork", r"collaborat"],
}

_COMPILED = {
    skill: [re.compile(rf"(?<![\w]){p}(?![\w])", re.IGNORECASE) for p in patterns]
    for skill, patterns in SKILLS.items()
}


def find_skills(text: str) -> set[str]:
    """Return the canonical skills mentioned in ``text``."""
    return {
        skill
        for skill, patterns in _COMPILED.items()
        if any(p.search(text) for p in patterns)
    }
