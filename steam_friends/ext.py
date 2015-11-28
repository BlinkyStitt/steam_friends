from __future__ import absolute_import, print_function

import celery
import celery.signals
import flask
import logging

from flask.ext import openid, redis


log = logging.getLogger(__name__)


class FlaskCelery(object):
    # todo: put this in an open source module

    def __init__(self, *args, **kwargs):
        self._tasks_to_register = {}

        self.app = kwargs.pop('app', None)
        if self.app is not None:
            self.init_app(self.app)

    def init_app(self, app):
        """Load the app's config into the celery object.

        .. IMPORTANT:: all tasks MUST be imported before init_app is called

        .. TODO:: how will we handle config reloading making it to celery?
        """
        app.config.setdefault('CELERY_ACCEPT_CONTENT', ['json', 'msgpack'])
        app.config.setdefault('CELERY_DEFAULT_EXCHANGE', app.import_name)
        app.config.setdefault('CELERY_DEFAULT_QUEUE', app.import_name)
        app.config.setdefault('CELERY_DEFAULT_ROUTING_KEY', app.import_name)
        app.config.setdefault('CELERY_EVENT_SERIALIZER', 'msgpack')
        app.config.setdefault('CELERY_IGNORE_RESULT', True)
        app.config.setdefault('CELERY_RESULT_EXCHANGE', "%s_celeryresults" % app.import_name)
        app.config.setdefault('CELERY_RESULT_SERIALIZER', 'msgpack')
        app.config.setdefault('CELERY_TASK_SERIALIZER', 'msgpack')
        app.config.setdefault('CELERYD_HIJACK_ROOT_LOGGER', False)

        # this has more in it than we need, but that's okay
        config_data = app.config

        # setup routing
        if not self._tasks_to_register:
            log.warning("No tasks registered")
        else:
            # for safety, all queues MUST be prefixed with the app name
            # todo: use NamedTuple?
            for task, (queue, exchange, routing_key) in self._tasks_to_register.iteritems():

                def prefix_if_needed(app, value):
                    """Return the app name or the value prefixed by the app name."""
                    app_prefix = app.import_name + '_'
                    if not value:
                        value = app.import_name
                    elif not value.startswith(app_prefix):
                        value = app_prefix + value
                    return value

                queue = prefix_if_needed(app, queue)
                exchange = prefix_if_needed(app, exchange)
                routing_key = prefix_if_needed(app, routing_key)

                if 'CELERY_ROUTES' not in config_data:
                    config_data['CELERY_ROUTES'] = {}

                if task not in config_data['CELERY_ROUTES']:
                    config_data['CELERY_ROUTES'][task] = {}

                if exchange:
                    config_data['CELERY_ROUTES'][task]['exchange'] = exchange
                if queue:
                    config_data['CELERY_ROUTES'][task]['queue'] = queue
                if routing_key:
                    config_data['CELERY_ROUTES'][task]['routing_key'] = routing_key

                # todo: also do celerybeat here

        # normally, this is created at import time. we make it here since we don't have config at import time
        self.celery_app = celery_app = celery.Celery(app.import_name)

        celery_app.conf.update(config_data)

        class ContextTask(celery_app.Task):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super(ContextTask, self).__call__(*args, **kwargs)
        celery_app.Task = ContextTask

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['celery'] = self

    def start(self):
        return self.celery_app.start()

    def task(self, *args, **kwargs):
        """Add a task to celery with the given exchange/queue/routing_key.

        This keeps us from creating the tasks at import time where our app config isn't available

        .. TODO:: use functools.wraps?
        """
        def task_decorator(func):
            # todo: what about routing keys? exchanges?
            exchange = kwargs.pop('exchange', None)
            queue = kwargs.pop('queue', None)
            routing_key = kwargs.pop('routing_key', None)

            # todo: use celery.current_app.task?
            func = celery.shared_task(*args, **kwargs)(func)

            self._tasks_to_register[func.name] = (queue, exchange, routing_key)

            return func
        return task_decorator

    @property
    def tasks(self):
        # if you try to use celery outside of current_app, it isn't configured!
        return flask.current_app.extensions['celery'].celery_app.tasks

    def get_task(self, name):
        # needed because we can't use the functions directly since we don't build celery app at import time
        if '.' not in name:
            # todo: this seems like a bad default
            name = 'steam_friends.models.' + name
        return self.tasks[name]


flask_celery = FlaskCelery()

flask_redis = redis.FlaskRedis()

oid = openid.OpenID(safe_roots=[])
