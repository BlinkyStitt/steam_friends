steam_friends
=============


Developing
----------

$ virtualenv env
$ . env/bin/activate
$ pip install -r requirements-dev.txt
$ npm install && bower install

$ cd static
$ grunt

$ STEAMODD_API_KEY=X STEAM_FRIENDS_SECRET_KEY=Y STEAM_FRIENDS_DEBUG=1 ./serve.py

$ open http://127.0.0.1:10000/

Testing
----------

$ virtualenv env
$ . env/bin/activate
$ pip install -r requirements-tests.txt
$ STEAMODD_API_KEY=X STEAM_FRIENDS_SECRET_KEY=Y py.test


Production
----------

Setup nginx to proxy your domain to port 10000

$ virtualenv env
$ env/bin/pip install -r requirements.txt
$ STEAMODD_API_KEY=X STEAM_FRIENDS_SECRET_KEY=Y STEAM_FRIENDS_PROXY_FIX=1 ./env/bin/python ./serve.py
