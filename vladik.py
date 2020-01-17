from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import urllib
import os

status = 'none'
try:
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(urllib.parse.quote_plus(os.environ['constr'])),
                           echo=True)
    engine.connect()
except Exception:
    print('connection error')
    status = 'error'
else:
    print('connection is ok')
    status = engine.execute('select @@VERSION')

app = Flask('vladik', static_url_path='/static')


@app.route('/connection', methods=['GET', 'POST'])
def connection():
    resp = jsonify({'connection': str(status)})
    return resp


@app.route('/question', methods=['GET', 'POST'])
def question():
    resp = jsonify({
        'id': 0,
        'question': (
            'Здравствуй! Я Владик, давай познакомимся!'
            ' Мне 160 лет, а тебе?'
        ),
        'options': [
            '0-17',
            '18-30',
            '30-50',
            '50-160',
        ],
    })
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/question/<option>', methods=['GET', 'POST'])
def question_answer(option):
    if option in ['0-17', '18-30', '30-50', '50-160']:
        resp = jsonify({
            'id': 1,
            'question': (
                'Расскажи о цели своего визита, мне очень хочется,'
                ' чтобы я тебе понравился!'
            ),
            'options': [
                'путешествие с семьей',
                'отдых',
                'командировка',
            ],
        })
    else:
        resp = jsonify({
            'question': None
        })

    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/route', methods=['GET', 'POST'])
def route():
    resp = jsonify({
        'route': [
            {
                'name': 'Прогулка по набережной',
                'location': 'на набережной',
                'time': '10:00-11:00',
                'description': 'lorem ipsum',
                'img': 'static/hqdefault.jpg',
                'tags': ['hui', 'pizda', 'chlen']
            },
            {
                'name': 'Завтрак в кафе',
                'location': 'какое-нибудь кафе (придумать)',
                'time': '11:00-13:00',
                'description': 'lorem ipsum',
                'img': 'static/cafe.png',
                'tags': ['zalupa', 'cafe']
            },
        ],
    })
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/cookieTest/get/<option>', methods=['GET', 'POST'])
def cookie_test_get(option):
    cc = request.cookies.get(option)
    resp = jsonify({option: cc})
    return resp


@app.route('/cookieTest/set/<option>', methods=['GET', 'POST'])
def cookie_test_set(option):
    resp = jsonify({})
    resp.set_cookie(option, 'test123')
    return resp
