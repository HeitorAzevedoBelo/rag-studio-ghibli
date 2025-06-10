from flask import Flask, render_template, request, jsonify
from model import responder

app = Flask(__name__)

@app.route('/')
def portal():
    return render_template('index.html')

@app.route('/explorar', methods=['POST'])
def explorar():
    payload = request.get_json(force=True)
    consulta = payload.get('pergunta', '').strip()
    if not consulta:
        return jsonify({'erro': 'Pergunta ausente'}), 400
    try:
        resposta = responder(consulta)
        return jsonify({'pergunta': consulta, 'resposta': resposta})
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
