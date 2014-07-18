import datetime
from flask import Flask, jsonify, render_template, request
from .database import Song

app = Flask(__name__)


def serialize(obj):
    if isinstance(obj, Song):
        return {
            'vendor': obj.vendor.name,
            'number': obj.number,
            'title': obj.title,
            'singer': obj.singer,
        }

    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')

    return str(obj)

@app.route('/')
def index():
    dbm = app.config['dbm']
    return render_template('index.html', dbm=dbm)


@app.route('/songs/')
def songs():
    dbm = app.config['dbm']
    vendor = request.args.get('vendor')
    number = request.args.get('number')
    title = request.args.get('title')
    singer = request.args.get('singer')


    if vendor != 'ALL':
        vendor = dbm.get_vendor(vendor)
    else:
        vendor = None

    songs = dbm.get_songs(
        vendor=vendor, title=title, number=number, singer=singer, limit=100)

    return jsonify({
        'songs': [serialize(song) for song in songs],
    })


@app.route('/info')
def info():
    dbm = app.config['dbm']
    return jsonify({
        'last_updated': serialize(dbm.get_last_updated()),
    })


@app.route('/get_update/<after>/')
def get_update(after):
    dbm = app.config['dbm']
    songs = dbm.get_songs(after=after)
    updated = dbm.get_last_updated()

    return jsonify({
        'songs': [serialize(song) for song in songs],
        'updated': serialize(updated),
    })
