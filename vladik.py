from flask import Flask, jsonify
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import os

app = Flask('vladik', static_url_path='/static')

#engine = create_engine(os.environ['constr'], echo=True)

#meta = MetaData()

#students = Table(
 #   'places', meta,
#    Column('id', Integer, primary_key=True),
#    Column('name', String),
#    Column('description', String),
#)
#meta.create_all(engine)



@app.route('/question', methods=['GET', 'POST'])
def question():
    resp = jsonify({
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
