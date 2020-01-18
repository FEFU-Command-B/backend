import urllib
import os
from contextlib import suppress

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
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

class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    entries = relationship("RouteEntry", backref="route")


class RouteEntry(Base):
    __tablename__ = 'routeentries'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    type = Column(String, nullable=False)
    exclude_tags = Column(String)
    start = Column(Float)
    end = Column(Float)


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


def get_place(start, end, _type, exclude_tag, visited):
    query = dbsession.query(Place) \
        .filter_by(type=_type) \
        .filter(Place.opening_time <= start) \
        .filter(Place.closing_time >= end) \
        .filter(~Place.id.in_(visited))

    if exclude_tag:
        query = query.filter(~Place.tags.like(exclude_tag))

    return query.first()


def set_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = request.environ.get('HTTP_ORIGIN', 'localhost:3000')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


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
                'Отлично! Какой тип отдыха тебе по душе? Ты любишь'
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
                'Мне очень нравится узнавать тебя лучше! Я хочу узнать, с'
                ' кем ты приехал ко мне в гости?'
            ),
            'options': [
                'Я тут один',
                'Я приехал с семьёй',
                'Я путешествую с друзьями или второй половинкой',
            ],
        })

    else:
        resp = jsonify({
            'question': None
        })
    return resp


@app.route('/connection', methods=['GET', 'POST'])
def connection():
    resp = jsonify({'connection': str(status)})

    return set_headers(resp)


@app.route('/question', methods=['GET', 'POST'])
def question():
    current_question = request.cookies.get('current question', 'age')
    resp = get_question(current_question)
    resp.set_cookie('current question', 'age')
    return set_headers(resp)


@app.route('/question/<option>', methods=['GET', 'POST'])
def question_answer(option):
    current_question = request.cookies['current question']

    if current_question == 'age':
        resp = get_question('museum')
        resp.set_cookie('over 18', str('больше' in option))
        resp.set_cookie('current question', 'museum')

    elif current_question == 'museum':
        resp = get_question('company')
        resp.set_cookie('museum', str('Да' in option))
        resp.set_cookie('current question', 'company')

    elif current_question == 'company':
        resp = get_question(None)
        resp.set_cookie('family', str('семьёй' in option))
        resp.set_cookie('current question', str(None))

    else:
        resp = get_question(None)

    return set_headers(resp)


@app.route('/route', methods=['GET', 'POST'])
def route():
    can_drink = request.cookies.get('over 18') == 'True' and request.cookies.get('family') == 'False'

    if request.cookies.get('museum') == 'True':
        if can_drink:
            schedule = 'profound drinker'
        else:
            schedule = 'profound'
    else:
        if can_drink:
            schedule = 'fun drinker'
        else:
            schedule = 'fun'

    route = dbsession.query(Route).filter_by(name=schedule).first()

    route = []
    visited = []
    for entry in route.entries:
        place = get_place(entry.start, entry.end, entry.type, entry.exclude_tags, visited)
        if place is None:
            continue
        visited.append(place.id)
        route.append({
            'name': place.name,
            'location': place.location,
            'time': f'{entry.start.hour}:{entry.start.minute}-{entry.end.hour}:{entry.end.minute}',
            'description': place.description,
            'img': place.img,
            'tags': place.tags.split()
        })

    resp = jsonify({
        'route': route,
    })

    return set_headers(resp)
