from flask import Flask, request, jsonify

app = Flask(__name__)

stats = {
    "hits": 0,
    "misses": 0,
    "latencias": [],
    "consultas_totales": 0
}

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.json
    stats["consultas_totales"] += 1
    stats["latencias"].append(data.get("latencia", 0))
    if data.get("evento") == "hit":
        stats["hits"] += 1
    elif data.get("evento") == "miss":
        stats["misses"] += 1
    return jsonify({"status": "ok"})

@app.route('/resumen', methods=['GET'])
def resumen():
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
