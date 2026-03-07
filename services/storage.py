from pathlib import Path


def ensure_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)


def is_log_like_file(file_path: Path) -> bool:
    name = file_path.name.lower()

    return (
        file_path.is_file()
        and (
            name.endswith(".log")
            or name.endswith(".txt")
            or ".log." in name
        )
    )


def save_uploaded_file(uploaded_file, upload_dir: Path) -> Path:
    ensure_directory(upload_dir)

    destination = upload_dir / Path(uploaded_file.name).name

    with open(destination, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return destination


def list_uploaded_files(upload_dir: Path) -> list[Path]:
    ensure_directory(upload_dir)

    files = [
        f for f in upload_dir.iterdir()
        if is_log_like_file(f)
    ]

    return sorted(files, key=lambda x: x.name.lower())