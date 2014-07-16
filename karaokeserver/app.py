from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

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
        'songs': [{
            'vendor': song.vendor.name,
            'number': song.number,
            'title': song.title,
            'singer': song.singer,
        } for song in songs],
    })
