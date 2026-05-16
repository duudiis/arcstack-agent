from ..config import settings


class SecurityError(Exception):
    pass


def validate_command(command: str) -> None:
    pass


def validate_path(path: str) -> str:
    return path


def truncate_output(output: str, max_size: int | None = None) -> str:
    limit = max_size or settings.max_output_size
    if len(output) > limit:
        return output[:limit] + f"\n\n[Output truncated at {limit} bytes]"
    return output
