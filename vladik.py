from flask import Flask, jsonify

app = Flask('vladik')


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


@app.route('/route', methods=['GET', 'POST'])
def route():
    resp = jsonify({
        'route': [
            {
                'name': 'Прогулка по набережной',
                'location': 'на набережной',
                'time': '10:00-11:00',
                'description': 'lorem ipsum',
            },
            {
                'name': 'Завтрак в кафе',
                'location': 'какое-нибудь кафе (придумать)',
                'time': '11:00-13:00',
                'description': 'lorem ipsum',
            },
        ],
    })
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
