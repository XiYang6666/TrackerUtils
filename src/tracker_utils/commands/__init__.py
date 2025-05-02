from ..app import app


@app.callback()
def main(): ...


def load_commands():
    from . import (
        client_test,  # noqa: F401
        set_trackers,  # noqa: F401
        test,  # noqa: F401
    )
