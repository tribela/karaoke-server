import datetime
import os
from collections import defaultdict

from flask import Flask, g, jsonify, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from . import database

app = Flask(__name__)
db_session = None


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
    global db_session
    db_uri = os.getenv('DATABASE_URL')
    db_session = database.get_session(db_uri)


@app.teardown_appcontext
def shutdown_session(exception=None):
    global db_session
    db_session.remove()


@app.route('/')
def index():
    vendors = database.get_all_vendors(db_session)
    return render_template('index.html', vendors=vendors)


@app.route('/query_songs/')
def songs():
    vendor = request.args.get('vendor')
    query = request.args.get('query')

    if vendor != 'ALL':
        vendor = database.get_vendor(db_session, vendor)
    else:
        vendor = None

    songs = database.get_songs(
        db_session,
        vendor=vendor,
        query_str=query,
        limit=100)

    return jsonify({
        'songs': [serialize(song) for song in songs],
    })


@app.route('/anisongs/', methods=['GET'])
def animation_songs():
    songs = db_session.query(database.SpecialIndex).order_by(
        database.SpecialIndex.division).all()
    dic = defaultdict(list)

    for song in songs:
        dic[song.division].append(song)

    return render_template('anisong.html', songs=dic)




@app.route('/special_songs/', methods=['GET'])
def special_songs():
    songs = db_session.query(database.SpecialIndex).all()
    dic = defaultdict(list)

    for song in songs:
        dic[song.division].append(serialize_anime_song(song))

    return jsonify(dic)


@app.route('/info')
def info():
    return jsonify({
        'last_updated': serialize(database.get_last_updated(db_session)),
    })


@app.route('/get_update/<after>/')
def get_update(after):
    songs = database.get_songs(db_session, after=after)
    updated = database.get_last_updated(db_session)

    return jsonify({
        'songs': [serialize(song) for song in songs],
        'updated': serialize(updated),
    })
