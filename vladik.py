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
            route = museumyes
        else:
            route = museumno
    else:
        if can_drink:
            route = nomuseumyes
        else:
            route = nomuseumno

    resp = jsonify({
        'route': route,
    })

    return set_headers(resp)

museumno = [
    {
        'name': 'Набережная Цесаревича',
        'location': 'Набережная Цесаревича',
        'time': '9:00-10:00',
        'description': 'На набережной есть большая прогулочная зона, которая отлично подходит как для пеших прогулок, так и для катания на роликах и скейтбордах. В центре набережной расположена детская площадка в виде корабля, большая шахматная доска, «Кровать примирения» и «Мост любви».',
        'img': 'https://vladivostok-city.com/uploads/i/bg/54918ad3b96b57.26761311.1164.jpg',
        'tags': ['прогулка']
    },
    {
        'name': 'Five o\'clock',
        'location': 'Фокина 6',
        'time': '10:00-11:00',
        'description': 'Уютное кафе в центре города с вкуснейшей выпечкой.',
        'img': 'https://static.vl.ru/catalog/1461695004117_big_vlru.jpg',
        'tags': ['кафе', 'выпечка']
    },
    {
        'name': 'Музей Арсеньева',
        'location': 'Светланская 20',
        'time': '11:00-14:00',
        'description': 'Первый на Дальнем Востоке краеведческий музей, крупнейший музей Приморского края. В музее представлена история и природа Приморского края, собраны коллекции материалов о деятельности исследователей края — М.И. Венюкова, Н.М. Пржевальского и других, материалы по истории города, археологии и этнографии.',
        'img': 'https://primamedia.gcdn.co/f/main/1866/1865542.jpg?bf0a13973bbb232b83781c547eb8e77d',
        'tags': ['музей', "история"]
    },
    {
        'name': 'Супра',
        'location': 'Адмирала Фокина 1Б',
        'time': '14:00-15:00',
        'description': 'Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.',
        'img': 'https://media-cdn.tripadvisor.com/media/photo-s/11/ea/cd/b2/same-again.jpg',
        'tags': ['ресторан', "Грузия"]
    },
    {
        'name': 'Центр современного искусства "Заря"',
        'location': 'проспект 100-летия Владивостока 155',
        'time': '15:00-18:00',
        'description': 'Интересный музей, который подойдёт ценителям современного искусства.',
        'img': 'http://zaryavladivostok.ru/uploads/image/Copy%20of%201GS_8850.jpg',
        'tags': ['музей', "современное искусство"]
    },
    {
        'name': 'Zuma',
        'location': 'Фонтанная 2',
        'time': '18:00-19:00',
        'description': 'Один из самых лучших паназиатских ресторанов Дальнего Востока. В особенности понравится любителям экзотических блюд и морепродуктов.',
        'img': 'https://static.vl.ru/catalog/1478242472572_big_vlru.jpg',
        'tags': ['ресторан', "морепродукты"]
    },
]

museumyes = [
    {
        'name': 'Набережная Цесаревича',
        'location': 'Набережная Цесаревича',
        'time': '9:00-10:00',
        'description': 'На набережной есть большая прогулочная зона, которая отлично подходит как для пеших прогулок, так и для катания на роликах и скейтбордах. В центре набережной расположена детская площадка в виде корабля, большая шахматная доска, «Кровать примирения» и «Мост любви».',
        'img': 'https://vladivostok-city.com/uploads/i/bg/54918ad3b96b57.26761311.1164.jpg',
        'tags': ['прогулка']
    },
    {
        'name': 'Five o\'clock',
        'location': 'Фокина 6',
        'time': '10:00-11:00',
        'description': 'Уютное кафе в центре города с вкуснейшей выпечкой.',
        'img': 'https://static.vl.ru/catalog/1461695004117_big_vlru.jpg',
        'tags': ['кафе', 'выпечка']
    },
    {
        'name': 'Музей Арсеньева',
        'location': 'Светланская 20',
        'time': '11:00-14:00',
        'description': 'Первый на Дальнем Востоке краеведческий музей, крупнейший музей Приморского края. В музее представлена история и природа Приморского края, собраны коллекции материалов о деятельности исследователей края — М.И. Венюкова, Н.М. Пржевальского и других, материалы по истории города, археологии и этнографии.',
        'img': 'https://primamedia.gcdn.co/f/main/1866/1865542.jpg?bf0a13973bbb232b83781c547eb8e77d',
        'tags': ['музей', "история"]
    },
    {
        'name': 'Супра',
        'location': 'Адмирала Фокина 1Б',
        'time': '14:00-15:00',
        'description': 'Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.',
        'img': 'https://media-cdn.tripadvisor.com/media/photo-s/11/ea/cd/b2/same-again.jpg',
        'tags': ['ресторан', "Грузия"]
    },
    {
        'name': 'Центр современного искусства "Заря"',
        'location': 'проспект 100-летия Владивостока 155',
        'time': '15:00-18:00',
        'description': 'Интересный музей, который подойдёт ценителям современного искусства.',
        'img': 'http://zaryavladivostok.ru/uploads/image/Copy%20of%201GS_8850.jpg',
        'tags': ['музей', "современное искусство"]
    },
    {
        'name': 'Ательер',
        'location': 'Светланская 9',
        'time': '18:00-21:00',
        'description': 'Атмосферное место в центре Владивостока, где вы можете насладиться вкусными коктейлями.',
        'img': 'https://tabler.ru/images/admins/1/place/standard/4135.jpg',
        'tags': ['ресторан', "алкоголь"]
    },
]

nomuseumno = [
    {
        'name': 'Набережная Цесаревича',
        'location': 'Набережная Цесаревича',
        'time': '9:00-10:00',
        'description': 'На набережной есть большая прогулочная зона, которая отлично подходит как для пеших прогулок, так и для катания на роликах и скейтбордах. В центре набережной расположена детская площадка в виде корабля, большая шахматная доска, «Кровать примирения» и «Мост любви».',
        'img': 'https://vladivostok-city.com/uploads/i/bg/54918ad3b96b57.26761311.1164.jpg',
        'tags': ['прогулка']
    },
    {
        'name': 'Five o\'clock',
        'location': 'Фокина 6',
        'time': '10:00-11:00',
        'description': 'Уютное кафе в центре города с вкуснейшей выпечкой.',
        'img': 'https://static.vl.ru/catalog/1461695004117_big_vlru.jpg',
        'tags': ['кафе', 'выпечка']
    },
    {
        'name': 'Приморский Океанариум',
        'location': 'остров Русский',
        'time': '11:00-14:00',
        'description': 'В Приморском океанариуме посетители смогут познакомиться с масштабными экспозициями, отражающими представления о рождении вселенной, эволюции жизни в Океане, а также с современным разнообразием жизни в пресных и морских водах нашей планеты. Большинство этих экспозиций живые.',
        'img': 'https://static.vl.ru/catalog/1489370757567_big_vlru.jpg',
        'tags': ['развлечения', "природа"]
    },
    {
        'name': 'Супра',
        'location': 'Адмирала Фокина 1Б',
        'time': '14:00-15:00',
        'description': 'Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.',
        'img': 'https://media-cdn.tripadvisor.com/media/photo-s/11/ea/cd/b2/same-again.jpg',
        'tags': ['ресторан', "Грузия"]
    },
    {
        'name': 'Приморская сцена Мариинского театра',
        'location': 'Фастовская 20',
        'time': '15:00-18:00',
        'description': 'Приморская сцена Мариинского театра — театр оперы и балета во Владивостоке.',
        'img': 'http://zaryavladivostok.ru/uploads/image/Copy%20of%201GS_8850.jpg',
        'tags': ['театр']
    },
    {
        'name': 'Zuma',
        'location': 'Фонтанная 2',
        'time': '18:00-19:00',
        'description': 'Один из самых лучших паназиатских ресторанов Дальнего Востока. В особенности понравится любителям экзотических блюд и морепродуктов.',
        'img': 'https://static.vl.ru/catalog/1478242472572_big_vlru.jpg',
        'tags': ['ресторан', "морепродукты"]
    },
]

nomuseumyes = [
    {
        'name': 'Набережная Цесаревича',
        'location': 'Набережная Цесаревича',
        'time': '9:00-10:00',
        'description': 'На набережной есть большая прогулочная зона, которая отлично подходит как для пеших прогулок, так и для катания на роликах и скейтбордах. В центре набережной расположена детская площадка в виде корабля, большая шахматная доска, «Кровать примирения» и «Мост любви».',
        'img': 'https://vladivostok-city.com/uploads/i/bg/54918ad3b96b57.26761311.1164.jpg',
        'tags': ['прогулка']
    },
    {
        'name': 'Five o\'clock',
        'location': 'Фокина 6',
        'time': '10:00-11:00',
        'description': 'Уютное кафе в центре города с вкуснейшей выпечкой.',
        'img': 'https://static.vl.ru/catalog/1461695004117_big_vlru.jpg',
        'tags': ['кафе', 'выпечка']
    },
    {
        'name': 'Приморский Океанариум',
        'location': 'остров Русский',
        'time': '11:00-14:00',
        'description': 'В Приморском океанариуме посетители смогут познакомиться с масштабными экспозициями, отражающими представления о рождении вселенной, эволюции жизни в Океане, а также с современным разнообразием жизни в пресных и морских водах нашей планеты. Большинство этих экспозиций живые.',
        'img': 'https://static.vl.ru/catalog/1489370757567_big_vlru.jpg',
        'tags': ['развлечения', "природа"]
    },
    {
        'name': 'Супра',
        'location': 'Адмирала Фокина 1Б',
        'time': '14:00-15:00',
        'description': 'Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.Колорит этого грузинского курорта генацвале могут увидеть, оглянувшись вокруг себя: яркие краски, чача–фонтан, зелень, пальмы, привезенная из Тбилиси керамическая плитка, кран из Серных бань и, конечно же панорманый вид на бухту Золотой Рог.',
        'img': 'https://media-cdn.tripadvisor.com/media/photo-s/11/ea/cd/b2/same-again.jpg',
        'tags': ['ресторан', "Грузия"]
    },
    {
        'name': 'Приморская сцена Мариинского театра',
        'location': 'Фастовская 20',
        'time': '15:00-18:00',
        'description': 'Приморская сцена Мариинского театра — театр оперы и балета во Владивостоке.',
        'img': 'http://zaryavladivostok.ru/uploads/image/Copy%20of%201GS_8850.jpg',
        'tags': ['театр']
    },
    {
        'name': 'Ательер',
        'location': 'Светланская 9',
        'time': '18:00-21:00',
        'description': 'Атмосферное место в центре Владивостока, где вы можете насладиться вкусными коктейлями.',
        'img': 'https://tabler.ru/images/admins/1/place/standard/4135.jpg',
        'tags': ['ресторан', "алкоголь"]
    },
]
