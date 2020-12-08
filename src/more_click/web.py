# -*- coding: utf-8 -*-

"""Utilities for web applications."""

import importlib
from typing import Any, Mapping, Optional, TYPE_CHECKING, Union

import click

from .options import host_option, port_option, verbose_option, with_gunicorn_option, workers_option

if TYPE_CHECKING:
    import flask  # noqa
    import gunicorn.app.base  # noqa

__all__ = [
    'make_web_command',
    'make_gunicorn_app',
]


def make_web_command(
    app: Union[str, 'flask.Flask'],
    *,
    group: Optional[click.Group] = None,
    command_kwargs: Optional[Mapping[str, Any]] = None,
) -> click.Command:
    """Make a command for running a web application"""
    if group is None:
        group = click

    if isinstance(app, str):
        package_name, class_name = app.split(':')
        package = importlib.import_module(package_name)
        app = getattr(package, class_name)

    @group.command(**(command_kwargs or {}))
    @host_option
    @port_option
    @with_gunicorn_option
    @workers_option
    @verbose_option
    def web(host: str, port: str, with_gunicorn: bool, workers: int):
        """Run the web application."""
        if with_gunicorn:
            gunicorn_app = make_gunicorn_app(app, host, port, workers)
            gunicorn_app.run()
        else:
            app.run(host=host, port=port)

    return web


def make_gunicorn_app(
    app: 'flask.Flask',
    host: str,
    port: str,
    workers: int,
    **kwargs,
) -> 'gunicorn.app.base.BaseApplication':
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

    kwargs.update({
        'bind': f'{host}:{port}',
        'workers': workers,
    })

    return StandaloneApplication(kwargs)
