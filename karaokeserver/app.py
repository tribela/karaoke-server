import datetime
import os
from collections import defaultdict
from flask import Flask, g, jsonify, render_template, request
from . import database

app = Flask(__name__)


def serialize(obj):
    if isinstance(obj, database.Song):
        return {
            'vendor': obj.vendor.name,
            'number': obj.number,
            'title': obj.title,
            'singer': obj.singer,
        }

    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d %H:%M:%S.%f')

    return str(obj)


def serialize_anime_song(song):
    return {
        'title': song.title,
        'tj': song.number_tj,
        'ky': song.number_ky,
    }


@app.before_first_request
def initialize():
    app.config['DB_URI'] = app.config.get('DB_URI', None) or \
            os.getenv('DATABASE_URL')
    database.init_db(app.config['DB_URI'])


@app.before_request
def before_request():
    g.db_session = database.get_session(app.config['DB_URI'])


@app.teardown_appcontext
def shutdown_session(exception=None):
    g.db_session.remove()


@app.route('/')
def index():
    vendors = database.get_all_vendors(g.db_session)
    return render_template('index.html', vendors=vendors)


@app.route('/query_songs/')
def songs():
    vendor = request.args.get('vendor')
    query = request.args.get('query')

    if vendor != 'ALL':
        vendor = database.get_vendor(g.db_session, vendor)
    else:
        vendor = None

    songs = database.get_songs(
        g.db_session,
        vendor=vendor,
        query_str=query,
        limit=100)

    return jsonify({
        'songs': [serialize(song) for song in songs],
    })


@app.route('/anisongs/', methods=['GET'])
def animation_songs():
    songs = g.db_session.query(database.SpecialIndex).order_by(
        database.SpecialIndex.division).all()
    dic = defaultdict(list)

    for song in songs:
        dic[song.division].append(song)

    return render_template('anisong.html', songs=dic)




@app.route('/special_songs/', methods=['GET'])
def special_songs():
    songs = g.db_session.query(database.SpecialIndex).all()
    dic = defaultdict(list)

    for song in songs:
        dic[song.division].append(serialize_anime_song(song))

    return jsonify(dic)


@app.route('/info')
def info():
    return jsonify({
        'last_updated': serialize(database.get_last_updated(g.db_session)),
    })


@app.route('/get_update/<after>/')
def get_update(after):
    songs = database.get_songs(g.db_session, after=after)
    updated = database.get_last_updated(g.db_session)

    return jsonify({
        'songs': [serialize(song) for song in songs],
        'updated': serialize(updated),
    })
