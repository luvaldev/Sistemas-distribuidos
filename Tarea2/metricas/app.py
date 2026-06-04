from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# requerimientos 
stats = {
    "hits": 0, 
    "misses": 0, 
    "recoveries": 0,
    "retries": 0, 
    "dlq_count": 0, 
    "fallas_temporales": 0,
    "latencias": [], 
    "consultas_totales": 0
}

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.json
    evento = data.get("evento")
    
    if evento in ["hit", "miss", "recovery"]:
        stats["consultas_totales"] += 1
        stats["latencias"].append(data.get("latencia", 0))
    
    if evento == "hit": stats["hits"] += 1
    elif evento == "miss": stats["misses"] += 1
    elif evento == "recovery": stats["recoveries"] += 1
    elif evento == "retry": stats["retries"] += 1
    elif evento == "dlq": stats["dlq_count"] += 1
    elif evento == "falla_temporal": stats["fallas_temporales"] += 1

    return jsonify({"status": "ok"})

@app.route('/resumen', methods=['GET'])
def resumen():
    lat = stats["latencias"]
    
    throughput = stats["consultas_totales"] / 50.0 if stats["consultas_totales"] > 0 else 0 
    lat_p50 = np.percentile(lat, 50) if lat else 0
    lat_p95 = np.percentile(lat, 95) if lat else 0
    
    resumen_final = {
        "1_Throughput (req/sec aprox)": round(throughput, 2),
        "2_Latencia_p50_segundos": round(lat_p50, 4),
        "3_Latencia_p95_segundos": round(lat_p95, 4),
        "4_Total_Procesadas_Exito": stats["consultas_totales"],
        "5_Hits_Cache": stats["hits"],
        "6_Misses_Normales": stats["misses"],
        "7_Recoveries_Exitosas_Tras_Fallo": stats["recoveries"],
        "8_Total_Reintentos_Kafka": stats["retries"],
        "9_Consultas_Perdidas_DLQ": stats["dlq_count"]
    }
    return jsonify(resumen_final)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)