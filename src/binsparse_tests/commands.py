from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_command(*args: str) -> CommandResult:
    completed = subprocess.run(
        args,
        check=False,
        capture_output=True,
        text=True,
    )
    result = CommandResult(
        args=tuple(args),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if result.returncode != 0:
        rendered = " ".join(result.args)
        raise RuntimeError(
            f"command failed: {rendered}\n"
            f"exit code: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result
