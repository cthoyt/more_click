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


@click.option()
@host_option
@port_option
def web(host: str, port: str):
    from .wsgi import app  # modify to point to your module-level flask.Flask instance
    app.run(host=host, port=port)
```

However, sometimes I want to make it possible to run via `gunicorn` from the CLI, so I would use the following
extensions to automatically determine if it should be run with Flask's development server or gunicorn.

```python
import click
from more_click import host_option, port_option, with_gunicorn_option, workers_option, run_app


@click.option()
@host_option
@port_option
@with_gunicorn_option
@workers_option
def web(host: str, port: str, with_gunicorn: bool, workers: int):
    from .wsgi import app  # modify to point to your module-level flask.Flask instance
    run_app(app=app, with_gunicorn=with_gunicorn, host=host, port=port, workers=workers)
```


