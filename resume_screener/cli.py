"""Command-line interface: rank a folder of resumes against a job description."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .parser import SUPPORTED_EXTENSIONS, extract_text
from .scorer import screen_resumes


def load_resumes(folder: Path) -> dict[str, str]:
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS)
    return {p.name: extract_text(p) for p in files}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="resume-screener", description="Rank resumes against a job description.")
    ap.add_argument("--job", required=True, type=Path, help="Job description file (.txt/.md/.pdf)")
    ap.add_argument("--resumes", required=True, type=Path, help="Folder of resumes (.pdf/.txt/.md)")
    ap.add_argument("--skills", help="Comma-separated required skills (default: detected from the job)")
    ap.add_argument("--top", type=int, default=0, help="Only show the top N candidates")
    ap.add_argument("--format", choices=["table", "json", "csv"], default="table")
    ap.add_argument("--output", type=Path, help="Write output to this file instead of stdout")
    return ap


def render_table(results) -> str:
    lines = [f"{'#':>2}  {'Candidate':<28} {'Score':>6}  {'Skills':>6}  Recommendation", "-" * 78]
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i:>2}  {r.name[:28]:<28} {r.score:>6.1f}  {r.skill_coverage:>6.0%}  {r.recommendation}"
        )
        if r.missing_skills:
            lines.append(f"    missing: {', '.join(r.missing_skills)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.resumes.is_dir():
        print(f"error: {args.resumes} is not a folder", file=sys.stderr)
        return 2
    resumes = load_resumes(args.resumes)
    if not resumes:
        print("error: no supported resumes found", file=sys.stderr)
        return 2
    skills = [s.strip() for s in args.skills.split(",")] if args.skills else None
    results = screen_resumes(extract_text(args.job), resumes, skills)
    if args.top:
        results = results[: args.top]

    if args.format == "json":
        out = json.dumps([r.to_dict() for r in results], indent=2)
    elif args.format == "csv":
        import io

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["rank", "name", "score", "skill_coverage", "matched", "missing", "email", "years"])
        for i, r in enumerate(results, 1):
            writer.writerow([i, r.name, r.score, r.skill_coverage, ";".join(r.matched_skills),
                             ";".join(r.missing_skills), r.email or "", r.years_experience or ""])
        out = buf.getvalue()
    else:
        out = render_table(results)

    if args.output:
        args.output.write_text(out, encoding="utf-8")
        print(f"Saved {len(results)} results to {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
