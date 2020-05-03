"""General utilities."""
import json
import typing


# --- Data storage files


def open_file(file: str) -> dict:
    """Open the file, if present, if not, return an empty dict."""
    try:
        with open(file) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_file(file: str, data: dict):
    """Save the file with modified data."""
    with open(file, 'w') as f:
        json.dump(data, f, indent=1)


def data_util(fun: typing.Callable, file: str) -> typing.Callable:
    """Wrap functions that need read/write access to data."""
    def wrapper(*args, **kwargs) -> typing.Any:
        """Open the file and save it again."""
        data = open_file(file)
        ret = fun(data, *args, **kwargs)
        save_file(file, data)
        return ret

    return wrapper
