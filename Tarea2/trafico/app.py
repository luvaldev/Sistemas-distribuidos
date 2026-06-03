import time, numpy as np, random, json, uuid
from kafka import KafkaProducer

ZONAS = ["Z1", "Z2", "Z3", "Z4", "Z5"]
TIPOS = ["Q1", "Q2", "Q3", "Q4", "Q5"]

# configuracion del productor kafka y se conecta al broker 'kafka' en el puerto 9092
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generar_consulta(distribucion):
    zona = random.choice(ZONAS) if distribucion == "uniforme" else ZONAS[min(np.random.zipf(2.0, 1)[0] - 1, 4)]
    tipo = random.choice(TIPOS)
    params = {"tipo": tipo, "zona": zona, "conf": "0.5"}
    if tipo == 'Q4': params["zona_b"] = random.choice(ZONAS)
    
    # identificador ; timestamp ; reintentos
    mensaje = {
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "retry_count": 0,
        "params": params
    }
    producer.send('consultas_topic', mensaje)

if __name__ == '__main__':
    print("esperando 45s para que el ecosistema y pandas carguen en la memoria...")
    time.sleep(45) 
    
    print("enviando 1000 consultas de trafico uniforme a Kafka...")
    for _ in range(1000): generar_consulta("uniforme")
    producer.flush() # los mensajes no se queden en el buffer del productor
        
    time.sleep(5)
    
    print("enviando 1000 consultas de trafico zipf a Kafka...")
    for _ in range(1000): generar_consulta("zipf")
    producer.flush()
        
    print("trafico terminado, los consumidores procesaran el backlog en kafka")