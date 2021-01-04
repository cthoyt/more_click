# more_click

<a href="https://pypi.org/project/more_click">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/more_click" />
</a>
<a href="https://pypi.org/project/more_click">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/more_click" />
</a>
<a href="https://github.com/cthoyt/more_click/blob/main/LICENSE">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/more_click" />
</a>
<a href="https://zenodo.org/badge/latestdoi/319609575">
    <img src="https://zenodo.org/badge/319609575.svg" alt="DOI">
</a>

Extra stuff for click I use in basically every repo

## More Options

The module `more_click.options` has several options (pre-defined instances of `click.option()`) that I use often. First,
`verbose_option` makes it easy to adjust the logger of your package using `-v`.

There are also several that are useful for web stuff, including

| Name                     | Type | Flag     |
| ------------------------ | ---- | -------- |
| `more_click.host_option` | str  | `--host` |
| `more_click.port_option` | str  | `--port` |

## Web Tools

In many packages, I've included a Flask web application in `wsgi.py`. I usually use the following form inside `cli.py`
file to import the web application and keep it insulated from other package-related usages:

```python
import click
from more_click import host_option, port_option


@click.command()
@click.option()
@host_option
@port_option
def web(host: str, port: str):
    from .wsgi import app  # modify to point to your module-level flask.Flask instance
    app.run(host=host, port=port)


if __name__ == '__main__':
    web()
```

However, sometimes I want to make it possible to run via `gunicorn` from the CLI, so I would use the following
extensions to automatically determine if it should be run with Flask's development server or gunicorn.

```python
import click
from more_click import host_option, port_option, with_gunicorn_option, workers_option, run_app


@click.command()
@click.option()
@host_option
@port_option
@with_gunicorn_option
@workers_option
def web(host: str, port: str, with_gunicorn: bool, workers: int):
    from .wsgi import app  # modify to point to your module-level flask.Flask instance
    run_app(app=app, with_gunicorn=with_gunicorn, host=host, port=port, workers=workers)


if __name__ == '__main__':
    web()
```

For ultimate lazy mode, I've written a wrapper around the second:

```python
from more_click import make_web_command

web = make_web_command('myapp.wsgi:app')

if __name__ == '__main__':
    web()
```

This uses a standard `wsgi`-style string to locate the app, since you don't want to be eagerly importing the app in your
CLI since it might rely on optional dependencies like Flask. If your CLI has other stuff, you can include the web
command in a group like:

```python
import click
from more_click import make_web_command


@click.group()
def main():
    """My awesome CLI."""


make_web_command('myapp.wsgi:app', group=main)

if __name__ == '__main__':
    main()
```
