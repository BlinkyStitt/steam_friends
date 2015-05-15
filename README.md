steam_friends
=============


Developing
----------

Initial Setup::

    virtualenv env
    . env/bin/activate
    pip install -r requirements-dev.txt
    export PATH=$(pwd)/static/node_modules/.bin:$PATH
    cd static
    npm install && bower install

Before Developing::

    export PATH=$(pwd)/static/node_modules/.bin:$PATH
    . env/bin/activate
    pip install -r requirements-dev.txt

Building static files::

    cd static
    grunt

Running the app::

    ./dev.py

    open http://127.0.0.1:10000/


Testing
----------

Running the python tests::

    virtualenv env
    . env/bin/activate
    pip install -r requirements-tests.txt
    py.test


Production
----------

Setup nginx to proxy your domain to port 10000

Then run the app::

    virtualenv env
    env/bin/pip install -r requirements-prod.txt
    uwsgi --buffer-size 8192 --master --processes 4 --threads 2 --socket 0.0.0.0:10000 --stats 127.0.0.1:10001 --wsgi-file prod.py

