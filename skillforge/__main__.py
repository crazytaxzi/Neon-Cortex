from __future__ import annotations

import argparse
from pathlib import Path

from .core import create_skill, validate_skill


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillforge",
        description="Create or validate canonical Neon Cortex skills.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new skill")
    create_parser.add_argument("name", help="Human-readable skill name")
    create_parser.add_argument(
        "--description",
        default="A new Neon Cortex skill",
        help="Short skill description",
    )
    create_parser.add_argument(
        "--root",
        default="skills",
        help="Directory that contains skill packages (default: skills)",
    )

    validate_parser = subparsers.add_parser("validate", help="Validate a skill package")
    validate_parser.add_argument("path", type=Path, help="Path to a skill directory")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "create":
        try:
            skill_dir = create_skill(args.name, args.description, root=args.root)
        except (FileExistsError, ValueError) as exc:
            print(f"error: {exc}")
            return 1
        print(f"Skill created at {skill_dir.resolve()}")
        return 0

    errors = validate_skill(args.path)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1

    print(f"Skill is valid: {args.path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
