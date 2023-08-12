# -*- coding: utf-8 -*-

"""Utilities for web applications."""

import importlib
import sys
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Union

import click

from .options import flask_debug_option, gunicorn_timeout_option, verbose_option, with_gunicorn_option, workers_option,with_uvicorn_option

if TYPE_CHECKING:
    import flask  # noqa
    import gunicorn.app.base  # noqa

__all__ = [
    "make_web_command",
    "run_app",
    "make_gunicorn_app",
]


def make_web_command(
    app: Union[str, "flask.Flask", Callable[[], "flask.Flask"]],
    *,
    group: Optional[click.Group] = None,
    command_kwargs: Optional[Mapping[str, Any]] = None,
    default_port: Union[None, str, int] = None,
    default_host: Optional[str] = None,
) -> click.Command:
    """Make a command for running a web application."""
    if group is None:
        group = click
    if isinstance(default_port, str):
        default_port = int(default_port)

    @group.command(**(command_kwargs or {}))
    @click.option("--host", type=str, default=default_host or "0.0.0.0", help="Flask host.", show_default=True)
    @click.option("--port", type=int, default=default_port or 5000, help="Flask port.", show_default=True)
    @with_gunicorn_option
    @with_uvicorn_option
    @workers_option
    @verbose_option
    @gunicorn_timeout_option
    @flask_debug_option
    def web(
        host: str,
        port: str,
        with_gunicorn: bool,
        with_uvicorn: bool,
        workers: int,
        debug: bool,
        timeout: Optional[int],
    ):
        """Run the web application."""
        import flask

        nonlocal app
        if isinstance(app, str):
            if app.count(":") != 1:
                raise ValueError(
                    "there should be exactly one colon in the string pointing to"
                    " an app like modulename.submodulename:appname_in_module"
                )
            package_name, class_name = app.split(":", 1)
            package = importlib.import_module(package_name)
            app = getattr(package, class_name)
            if isinstance(app, flask.Flask):
                pass
            elif callable(app):
                app = app()
            else:
                raise TypeError(
                    "when using a string path with more_click.make_web_command(),"
                    " it's required that it points to either an instance of a Flask"
                    " application or a 0-argument function that returns one."
                )
        elif isinstance(app, flask.Flask):
            pass
        elif callable(app):
            app = app()
        else:
            raise TypeError(
                "when using more_click.make_web_command(), the app argument should either"
                " be an instance of a Flask app, a 0-argument function that returns a Flask app,"
                " a string pointing to a Flask app in a python module, or a string pointing to a"
                " 0-argument function that returns a Flask app"
            )

        if debug and with_gunicorn:
            click.secho("can not use --debug and --with-gunicorn together")
            return sys.exit(1)

        run_app(
            app=app,
            host=host,
            port=port,
            workers=workers,
            with_gunicorn=with_gunicorn,
            with_uvicorn=with_uvicorn,
            debug=debug,
            timeout=timeout,
        )

    return web


def run_app(
    app: "flask.Flask",
    with_gunicorn: bool = False,
    with_uvicorn: bool = False,
    host: Optional[str] = None,
    port: Union[None, int, str] = None,
    workers: Optional[int] = None,
    timeout: Optional[int] = None,
    debug: bool = False,
):
    """Run the application."""
    if with_gunicorn:
        if host is None or port is None or workers is None:
            raise ValueError("must specify host, port, and workers.")
        if debug:
            raise ValueError("can not use debug=True with with_gunicorn=True")
        gunicorn_app = make_gunicorn_app(
            app,
            host=host,
            port=port,
            workers=workers,
            timeout=timeout,
        )
        gunicorn_app.run()
    elif with_uvicorn:
        if host is None or port is None or workers is None:
            raise ValueError("must specify host and port for uvicorn.")
        if debug:
            raise ValueError("can not use debug=True with with_uvicorn=True")

        import uvicorn

        uvicorn.run(app, host=host, port=int(port), log_level="info")
    else:
        app.run(host=host, port=port, debug=debug)


def make_gunicorn_app(
    app: "flask.Flask",
    host: str,
    port: Union[str, int],
    workers: int,
    timeout: Optional[int] = None,
    **kwargs,
) -> "gunicorn.app.base.BaseApplication":
    """Make a GUnicorn App."""
    from gunicorn.app.base import BaseApplication

    class StandaloneApplication(BaseApplication):
        def __init__(self, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def init(self, parser, opts, args):
            pass

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    kwargs.update(
        {
            "bind": f"{host}:{port}",
            "workers": workers,
        }
    )
    if timeout is not None:
        kwargs["timeout"] = timeout

    return StandaloneApplication(kwargs)
