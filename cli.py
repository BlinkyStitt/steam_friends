#!/usr/bin/env python
from __future__ import absolute_import

import logging
import shlex
import sys

import click

from steam_friends import app


# similar to flask.app.Flask.debug_log_format
debug_log_format = (
    '-' * 80 + '\n' +
    '%(levelname)s in %(name)s [%(pathname)s:%(lineno)d]:\n' +
    '%(message)s\n' +
    '-' * 80
)


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=debug_log_format)
logging.getLogger('celery').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

log = logging.getLogger(__name__)


@click.group()
@click.option('--env', default='dev', type=click.Choice(['dev', 'prod', 'test']))
@click.pass_context
def cli(ctx, env):
    """Manage steam_friends."""
    ctx.obj = app.create_app(app_env=env)


@cli.command()
@click.argument("celery_args", default="worker")
@click.pass_obj
def celery(obj, celery_args):
    """Run celery. By default starts a worker."""
    celery_ext = obj.extensions['celery']

    # todo: should this be inside `start`?
    sys.argv = [str(celery_ext)] + shlex.split(celery_args)
    log.debug(" ".join(sys.argv))

    celery_ext.start()


@cli.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=10000, type=click.INT)
@click.pass_obj
def http(obj, host, port):
    """Run a development http server."""

    log.info("Starting %s for development at http://%s:%s", obj, host, port)
    if obj.debug:
        obj.logger.warning("Application debugging enabled! Be sure not to expose this to the Internet!")

    obj.run(host=host, port=port)


if __name__ == '__main__':
    cli(auto_envvar_prefix='STEAM_FRIENDS')
