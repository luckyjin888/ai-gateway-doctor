from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    check: str
    status: str
    summary: str
    evidence: str = ""
    remediation: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

