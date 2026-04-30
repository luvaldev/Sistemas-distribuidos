from flask import Flask, request, jsonify
import redis, requests, json, time

app = Flask(__name__)
r = redis.Redis(host='redis-cache', port=6379, decode_responses=True)

URL_RESPUESTAS = "http://servicio-respuestas:5001/procesar"
URL_METRICAS = "http://servicio-metricas:5002/registrar"

@app.route('/consulta', methods=['GET'])
def consulta():
    inicio = time.time()
    tipo = request.args.get('tipo')
    zona = request.args.get('zona')
    conf = request.args.get('conf', '0.0')
    
    if tipo == 'Q4':
        zona_b = request.args.get('zona_b', 'Z2')
        cache_key = f"compare:density:{zona}:{zona_b}:conf={conf}"
    elif tipo == 'Q5':
        bins = request.args.get('bins', '5')
        cache_key = f"confidence_dist:{zona}:bins={bins}"
    else:
        cache_key = f"{tipo.lower()}:{zona}:conf={conf}"
        
    resultado_cache = r.get(cache_key)
    
    if resultado_cache:
        latencia = time.time() - inicio
        requests.post(URL_METRICAS, json={"evento": "hit", "latencia": latencia})
        return jsonify(json.loads(resultado_cache))
    else:
        resp = requests.get(URL_RESPUESTAS, params=request.args).json()
        r.setex(cache_key, 60, json.dumps(resp))
        latencia = time.time() - inicio
        requests.post(URL_METRICAS, json={"evento": "miss", "latencia": latencia})
        return jsonify(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
