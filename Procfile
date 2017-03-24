web: uwsgi --master --die-on-term --module karaokeserver.app:app --http-socket :5000
dev: FLASK_APP=karaokeserver/app.py FLASK_DEBUG=1 flask run -h 0.0.0.0 -p 5000
worker: python worker.py
