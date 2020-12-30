# -*- coding: utf-8 -*-

"""More click options."""

import logging
import multiprocessing

import click

__all__ = [
    'verbose_option',
    'host_option',
    'port_option',
    'with_gunicorn_option',
    'workers_option',
]

LOG_FMT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'


def _debug_callback(_ctx, _param, value):
    if not value:
        logging.basicConfig(level=logging.WARNING, format=LOG_FMT, datefmt=LOG_DATEFMT)
    elif value == 1:
        logging.basicConfig(level=logging.INFO, format=LOG_FMT, datefmt=LOG_DATEFMT)
    else:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FMT, datefmt=LOG_DATEFMT)


verbose_option = click.option(
    '-v', '--verbose',
    count=True,
    callback=_debug_callback,
    expose_value=False,
    help="Enable verbose mode. More -v's means more verbose.",
)


def _number_of_workers() -> int:
    """Calculate the default number of workers."""
    return (multiprocessing.cpu_count() * 2) + 1


host_option = click.option('--host', type=str, default='0.0.0.0', help='Flask host.', show_default=True)
port_option = click.option('--port', type=int, default=5000, help='Flask port.', show_default=True)
with_gunicorn_option = click.option('--with-gunicorn', is_flag=True, help='Use gunicorn instead of flask dev server')
workers_option = click.option('--workers', type=int, default=_number_of_workers(), help='Number of workers (when using --with-gunicorn)')
