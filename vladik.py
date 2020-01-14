from flask import Flask, jsonify

app = Flask('yarmarka')


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
