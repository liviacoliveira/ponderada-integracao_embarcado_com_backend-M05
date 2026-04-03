from flask import Flask, render_template, request, jsonify, redirect, url_for
import database
try:
    from . import config
except ImportError:
    import config

app = Flask(__name__)

# Inicializa o banco de dados na primeira execução
with app.app_context():
    database.init_db()

def responder(template, data=None, status=200):
    """Auxiliar para responder em JSON ou HTML baseado no parâmetro ?formato=json."""
    formato = request.args.get('formato')
    if formato == 'json':
        return jsonify(data), status
    return render_template(template, **(data if data else {})), status

@app.route('/')
def index():
    """Painel principal — últimas 10 leituras."""
    leituras = database.listar_leituras(limite=10)
    estatisticas = database.obter_estatisticas()
    
    # Prepara dados para o gráfico para evitar lógica complexa no Jinja
    chart_data = {
        "labels": [l['timestamp'].split(' ')[1][:5] for l in leituras][::-1] if leituras else [],
        "temps": [l['temperatura'] for l in leituras][::-1] if leituras else [],
        "umids": [l['umidade'] for l in leituras][::-1] if leituras else []
    }
    
    return responder('index.html', {
        'leituras': leituras, 
        'estatisticas': estatisticas,
        'chart_data': chart_data
    })

@app.route('/leituras', methods=['GET'])
def listar():
    """Histórico completo com paginação básica."""
    limite = request.args.get('limite', default=50, type=int)
    leituras = database.listar_leituras(limite=limite)
    return responder('historico.html', {'leituras': leituras, 'limite': limite})

@app.route('/leituras', methods=['POST'])
def criar():
    """Recebe JSON do Arduino / simulador."""
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    
    try:
        temp = dados.get('temperatura')
        umid = dados.get('umidade')
        pres = dados.get('pressao')
        
        id_inserido = database.inserir_leitura(temp, umid, pres)
        return jsonify({"id": id_inserido, "status": "sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/leituras/<int:id>', methods=['GET'])
def detalhe(id):
    """Exibe uma leitura específica."""
    leitura = database.buscar_leitura(id)
    if not leitura:
        return responder('404.html', {"erro": "Leitura não encontrada"}, 404)
    return responder('editar.html', {'leitura': leitura})

@app.route('/leituras/<int:id>', methods=['PUT', 'POST'])
def atualizar(id):
    """Atualiza campos de uma leitura. (Aceita POST para facilitar forms HTML)."""
    if request.method == 'POST' and request.form.get('_method') != 'PUT':
        # Se for um POST normal de form, tratamos como UPDATE via form
        dados = {
            "temperatura": request.form.get('temperatura', type=float),
            "umidade": request.form.get('umidade', type=float),
            "pressao": request.form.get('pressao', type=float)
        }
    else:
        # Se for PUT real ou simulado via JSON
        dados = request.get_json() if request.is_json else request.form.to_dict()
        if '_method' in dados: dados.pop('_method')

    sucesso = database.atualizar_leitura(id, dados)
    
    if request.args.get('formato') == 'json':
        return jsonify({"sucesso": sucesso}), 200 if sucesso else 404
    
    return redirect(url_for('index'))

@app.route('/leituras/<int:id>/deletar', methods=['POST', 'DELETE'])
def deletar(id):
    """Remove uma leitura do banco."""
    sucesso = database.deletar_leitura(id)
    
    if request.args.get('formato') == 'json' or request.method == 'DELETE':
        return jsonify({"sucesso": sucesso}), 200 if sucesso else 404
        
    return redirect(url_for('index'))

@app.route('/api/estatisticas')
def estatisticas():
    """Média, mín e máx do período (Sempre JSON conforme tabela)."""
    data = database.obter_estatisticas()
    return jsonify(data)

if __name__ == '__main__':
    # Usa configurações do config.py
    app.run(
        debug=getattr(config, 'DEBUG', True), 
        port=getattr(config, 'FLASK_PORT', 5000)
    )
