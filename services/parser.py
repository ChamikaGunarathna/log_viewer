import re
from pathlib import Path


LOG_PATTERN = re.compile(
    r"^\s*"
    r"(?P<level>[A-Z]+)\s*\|\s*"
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s*\|\s*"
    r"(?P<user>.*?)\s*\|\s*"
    r"(?P<module>.*?)\s*\|\s*"
    r"(?P<message>.*)$"
)


def parse_log_file(file_path: Path) -> list[dict]:
    entries: list[dict] = []

    if not file_path.exists():
        return entries

    current_entry = None

    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            match = LOG_PATTERN.match(line)

            if match:
                if current_entry is not None:
                    entries.append(current_entry)

                current_entry = {
                    "level": match.group("level").strip(),
                    "timestamp": match.group("timestamp").strip(),
                    "user": match.group("user").strip(),
                    "module": match.group("module").strip(),
                    "message": match.group("message"),
                }
            else:
                if current_entry is not None:
                    current_entry["message"] += "\n" + line
                else:
                    entries.append(
                        {
                            "level": "RAW",
                            "timestamp": "",
                            "user": "",
                            "module": "",
                            "message": line,
                        }
                    )

    if current_entry is not None:
        entries.append(current_entry)

    return entries