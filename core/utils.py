from datetime import datetime
from pathlib import Path


def media_upload_path(prefix: str, filename: str) -> str:
    now = datetime.now()
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    return f"{prefix}/{now:%Y/%m/%d}/{stem}-{now:%Y%m%d%H%M%S}{suffix}"
