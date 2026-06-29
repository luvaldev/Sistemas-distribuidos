from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

zonas_km2 = {"Z1": 14.4, "Z2": 99.4, "Z3": 133.0, "Z4": 22.4, "Z5": 197.0}
zonas_bbox = {
    "Z1": {"lat_min": -33.445, "lat_max": -33.420, "lon_min": -70.640, "lon_max": -70.600},
    "Z2": {"lat_min": -33.420, "lat_max": -33.390, "lon_min": -70.600, "lon_max": -70.550},
    "Z3": {"lat_min": -33.530, "lat_max": -33.490, "lon_min": -70.790, "lon_max": -70.740},
    "Z4": {"lat_min": -33.470, "lat_max": -33.430, "lon_min": -70.670, "lon_max": -70.630},
    "Z5": {"lat_min": -33.470, "lat_max": -33.430, "lon_min": -70.810, "lon_max": -70.760}
}

print("cargando dataset")
try:
    df = pd.read_csv('santiago_buildings.csv')
    datos = {}
    for z_id, bbox in zonas_bbox.items():
        filtro = ((df['latitude'] >= bbox['lat_min']) & (df['latitude'] <= bbox['lat_max']) &
                  (df['longitude'] >= bbox['lon_min']) & (df['longitude'] <= bbox['lon_max']))
        datos[z_id] = df[filtro][['area_in_meters', 'confidence']].rename(
            columns={'area_in_meters': 'area'}
        ).to_dict('records')
    print("dataset cargado perfectamente")
except Exception as e:
    print(f"error fatal cargando csv: {e}")
    datos = {z: [] for z in zonas_bbox.keys()}

def q1_count(zona, conf):
    return sum(1 for r in datos.get(zona, []) if r["confidence"] >= conf)

def q2_area(zona, conf):
    areas = [r["area"] for r in datos.get(zona, []) if r["confidence"] >= conf]
    if not areas: return {"avg_area": 0, "total_area": 0, "n": 0}
    return {"avg_area": float(np.mean(areas)), "total_area": sum(areas), "n": len(areas)}

def q3_density(zona, conf):
    return {"density": q1_count(zona, conf) / zonas_km2.get(zona, 1.0)}

def q4_compare(zona_a, zona_b, conf):
    da, db = q3_density(zona_a, conf)["density"], q3_density(zona_b, conf)["density"]
    return {"zone_a": da, "zone_b": db, "winner": zona_a if da > db else zona_b}

def q5_confidence_dist(zona, bins):
    scores = [r["confidence"] for r in datos.get(zona, [])]
    if not scores: return {"distribution": []}
    counts, edges = np.histogram(scores, bins=bins, range=(0, 1))
    dist = [{"bucket": i, "min": float(edges[i]), "max": float(edges[i+1]), "count": int(counts[i])} for i in range(bins)]
    return {"distribution": dist}

# simulacion de fallas
falla_simulada = False

@app.route('/toggle-falla', methods=['POST'])
def toggle_falla():
    global falla_simulada
    falla_simulada = not falla_simulada
    estado = "Activada (Devolviendo error 503)" if falla_simulada else "Desactivada (Operando normal)"
    return jsonify({"status": f"Simulación de falla {estado}"})

@app.route('/procesar', methods=['GET'])
def procesar():
    global falla_simulada
    
    if falla_simulada:
        return jsonify({"error": "falla temporal simulada en el servicio"}), 503

    tipo = request.args.get('tipo')
    zona = request.args.get('zona')
    conf = float(request.args.get('conf', 0.0))
    
    if tipo == 'Q1': res = {"count": q1_count(zona, conf)}
    elif tipo == 'Q2': res = q2_area(zona, conf)
    elif tipo == 'Q3': res = q3_density(zona, conf)
    elif tipo == 'Q4': res = q4_compare(zona, request.args.get('zona_b', 'Z2'), conf)
    elif tipo == 'Q5': res = q5_confidence_dist(zona, int(request.args.get('bins', 5)))
    else: res = {"error": "tipo desconocido"}
    
    res["_simulacion_peso"] = "X" * (2 * 1024 * 1024)
    
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
