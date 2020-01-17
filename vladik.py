from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, Column, Integer, String, Time, MetaData
from sqlalchemy.ext.declarative import declarative_base
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



Base = declarative_base()


class Place(Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    location = Column(String, nullable=False)
    img = Column(String, nullable=False)
    type = Column(String, nullable=False)
    tags = Column(String)
    opening_time = Column(Time)
    closing_time = Column(Time)


def set_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'


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
    set_headers(resp)
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

    set_headers(resp)
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
                'description': 'Ut sed velit at ante aliquam pretium sit amet ut felis. Nunc et turpis orci. Aenean lorem sapien, euismod nec euismod porta, pellentesque convallis nisl. Aliquam nulla ligula, gravida et consequat et, ultricies sit amet velit. Sed facilisis felis est, at feugiat elit molestie et. Nunc quis egestas felis. Suspendisse egestas vehicula nibh, eget convallis ligula eleifend eget. Mauris ac lacus ut risus euismod laoreet ac eget mauris. Cras consequat rhoncus iaculis. Praesent nec dictum mi. Donec nec augue et quam mattis eleifend. Nulla tincidunt ligula sed lobortis condimentum. Nulla fringilla lacus sit amet diam aliquet, in suscipit ipsum vulputate. Integer scelerisque tortor orci. Proin eget lectus mauris. Vestibulum finibus cursus vehicula. Ut sed velit at ante aliquam pretium sit amet ut felis. Nunc et turpis orci. Aenean lorem sapien, euismod nec euismod porta, pellentesque convallis nisl. Aliquam nulla ligula, gravida et consequat et, ultricies sit amet velit. Sed facilisis felis est, at feugiat elit molestie et. Nunc quis egestas felis. Suspendisse egestas vehicula nibh, eget convallis ligula eleifend eget. Mauris ac lacus ut risus euismod laoreet ac eget mauris. Cras consequat rhoncus iaculis. Praesent nec dictum mi. Donec nec augue et quam mattis eleifend. Nulla tincidunt ligula sed lobortis condimentum. Nulla fringilla lacus sit amet diam aliquet, in suscipit ipsum vulputate. Integer scelerisque tortor orci. Proin eget lectus mauris. Vestibulum finibus cursus vehicula. Ut sed velit at ante aliquam pretium sit amet ut felis. Nunc et turpis orci. Aenean lorem sapien, euismod nec euismod porta, pellentesque convallis nisl. Aliquam nulla ligula, gravida et consequat et, ultricies sit amet velit. Sed facilisis felis est, at feugiat elit molestie et. Nunc quis egestas felis. Suspendisse egestas vehicula nibh, eget convallis ligula eleifend eget. Mauris ac lacus ut risus euismod laoreet ac eget mauris. Cras consequat rhoncus iaculis. Praesent nec dictum mi. Donec nec augue et quam mattis eleifend. Nulla tincidunt ligula sed lobortis condimentum. Nulla fringilla lacus sit amet diam aliquet, in suscipit ipsum vulputate. Integer scelerisque tortor orci. Proin eget lectus mauris. Vestibulum finibus cursus vehicula.',
                'img': 'static/cafe.png',
                'tags': ['zalupa', 'cafe']
            },
        ],
    })
    set_headers(resp)
    return resp


@app.route('/cookieTest/get/<option>', methods=['GET', 'POST'])
def cookie_test_get(option):
    cc = request.cookies.get(option)
    resp = jsonify({option: cc})
    set_headers(resp)
    return resp


@app.route('/cookieTest/set/<option>', methods=['GET', 'POST'])
def cookie_test_set(option):
    resp = jsonify({})
    resp.set_cookie(option, 'test123')
    set_headers(resp)
    return resp
