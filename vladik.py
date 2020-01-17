import urllib
import os
from contextlib import suppress

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

status = 'none'
try:
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(urllib.parse.quote_plus(os.environ['constr'])),
                           echo=True)
    engine.connect()

    Session = sessionmaker(bind=engine)
    dbsession = Session()
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
    opening_time = Column(Float)
    closing_time = Column(Float)

Base.metadata.create_all(engine)


def get_place(start, end, type, exclude_tag, visited):
    query = dbsession.query(Place)\
        .filter_by(Place.type == type)\
        .filter_by(Place.opening_time <= start)\
        .filter_by(Place.closing_time >= end)\
        .filter_by(~Place.id.in_(visited))

    if exclude_tag:
        query = query.filter_by(~Place.tags.like(exclude_tag))

    return query.first()

def get_question(question_name):
    if question_name == 'age':
        resp = jsonify({
            'question': (
                'Привет, я Владик! Давай познакомимся?'
                ' Мне 160 лет, а тебе?'
            ),
            'options': [
                'Мне меньше 18',
                'Мне больше 18',
            ],
        })

    elif question_name == 'museum':
        resp = jsonify({
            'question': (
                'Отлично! Какой тип отдыза тебе по душе? Ты любишь'
                ' музеи? Я от них без ума!'
            ),
            'options': [
                'Да',
                'Нет',
            ],
        })

    elif question_name == 'company':
        resp = jsonify({
            'question': (
                'Мне ояень нравится узнавать тебя лучше! Я хочу узнать, с'
                ' кем ты приехал ко мне в гости?'
            ),
            'options': [
                'Я тут один',
                'Я приехал с семьёй',
                'Я путешествую с друзьями / второй половинкой',
            ],
        })

    else:
        resp = jsonify({
            'question': None
        })

    return resp


def set_headers(resp):
    with suppress(KeyError):
        resp.headers['Access-Control-Allow-Origin'] = request.environ['HTTP_ORIGIN']
    resp.headers['Access-Control-Allow-Credentials'] = 'true'


@app.route('/connection', methods=['GET', 'POST'])
def connection():
    resp = jsonify({'connection': str(status)})
    return resp


@app.route('/question', methods=['GET', 'POST'])
def question():
    current_question = request.cookies.get('current question', 'age')
    resp = get_question(current_question)
    resp.set_cookie('current question', 'age')
    set_headers(resp)
    return resp


@app.route('/question/<option>', methods=['GET', 'POST'])
def question_answer(option):
    current_question = request.cookies['current question']

    if current_question == 'age':
        resp = get_question('museum')
        resp.set_cookie('over 18', 'больше' in option)
        resp.set_cookie('current question', 'museum')

    elif current_question == 'museum':
        resp = get_question('company')
        resp.set_cookie('museum', 'Да' in option)
        resp.set_cookie('current question', 'company')

    elif current_question == 'company':
        resp = get_question(None)
        resp.set_cookie('family', 'семьёй' in option)
        resp.set_cookie('current question', None)

    else:
        resp = get_question(None)

    set_headers(resp)
    return resp


@app.route('/route', methods=['GET', 'POST'])
def route():
    can_drink = request.cookies['over 18'] == 'True' and request.cookies['family'] == 'False'
    if request.cookies['museum'] == 'True':
        schedule = (
            (9, 10, 'walk', None),
            (10, 11, 'food', 'alcohol'),
            (11, 14, 'museum', None),
            (14, 15, 'walk', None),
            (15, 18, 'museum', None),
            (18, 20, 'food', None if can_drink else 'alcohol'),
        )
    else:
        schedule = (
            (9, 10, 'walk', None),
            (10, 11, 'food', 'alcohol'),
            (11, 14, 'entartainment', None),
            (14, 15, 'walk', None),
            (15, 18, 'entertainment', None),
            (18, 20, 'food', None if can_drink else 'alcohol'),
        )

    route = []
    visited = []
    for args in schedule:
        place = get_place(*args, visited)
        if place is None:
            continue
        visited.append(place.id)
        route.append({
            'name': place.name,
            'location': place.location,
            'time': f'{args[0]}:00-{args[1]}:00',
            'description': place.description,
            'img': place.img,
            'tags': place.tags.split()
        })

    resp = jsonify({
        'route': route,
    })
    set_headers(resp)
    return resp
