import requests, time, numpy as np, random

URL_CACHE = "http://servicio-cache:5000/consulta"
ZONAS = ["Z1", "Z2", "Z3", "Z4", "Z5"]
TIPOS = ["Q1", "Q2", "Q3", "Q4", "Q5"]

def generar_consulta(distribucion):
    zona = random.choice(ZONAS) if distribucion == "uniforme" else ZONAS[min(np.random.zipf(2.0, 1)[0] - 1, 4)]
    tipo = random.choice(TIPOS)
    params = {"tipo": tipo, "zona": zona, "conf": "0.5"}
    if tipo == 'Q4': params["zona_b"] = random.choice(ZONAS)
    try: requests.get(URL_CACHE, params=params)
    except: pass

if __name__ == '__main__':
    print("esperando 45s para que pandas logre cargar los 2gb de csv en memoria")
    time.sleep(45) 
    
    print("enviando 1000 consultas de trafico uniforme")
    for _ in range(1000): generar_consulta("uniforme")
        
    time.sleep(5)
    
    print("enviando 1000 consultas de trafico zipf")
    for _ in range(1000): generar_consulta("zipf")
        
    print("trafico finalizado http://localhost:5002/resumen para ver resultados")
