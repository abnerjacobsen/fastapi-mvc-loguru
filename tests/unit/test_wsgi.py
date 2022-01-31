import sys
import os

import mock
from das_sankhya.wsgi import run_wsgi


@mock.patch("das_sankhya.wsgi.ApplicationLoader")
def test_run_wsgi(loader_mock):
    run_wsgi("localhost", "5555", "2")
    loader_mock.assert_called_once()
    assert sys.argv == [
        "--gunicorn",
        "-c",
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../das_sankhya/config/gunicorn.conf.py"
            )
        ),
        "-w",
        "2",
        "-b localhost:5555",
        "das_sankhya.app.asgi:application"
    ]
