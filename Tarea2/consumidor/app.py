import redis, requests, json, time
from kafka import KafkaConsumer, KafkaProducer

r = redis.Redis(host='redis-cache', port=6379, decode_responses=True) # conexion a redis

URL_RESPUESTAS = "http://servicio-respuestas:5001/procesar"
URL_METRICAS = "http://servicio-metricas:5002/registrar"
MAX_RETRIES = 3

# enviar los mensajes que fallan
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# escucha el topico principal y reintentos
consumer = KafkaConsumer(
    'consultas_topic', 'reintentos_topic',
    bootstrap_servers=['kafka:9092'],
    group_id='consumidores-geo', 
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

print("consumidor kafka iniciado, esperando mensajes...")

for message in consumer:
    inicio = time.time()
    data = message.value
    params = data['params']
    tipo, zona, conf = params['tipo'], params['zona'], params.get('conf', '0.0')

    # recrear la llave de cache exactamente como en la primera tarea
    if tipo == 'Q4':
        zona_b = params.get('zona_b', 'Z2')
        cache_key = f"compare:density:{zona}:{zona_b}:conf={conf}"
    elif tipo == 'Q5':
        bins = params.get('bins', '5')
        cache_key = f"confidence_dist:{zona}:bins={bins}"
    else:
        cache_key = f"{tipo.lower()}:{zona}:conf={conf}"

    # revisar si la respuesta ya esta en redis
    resultado_cache = r.get(cache_key)

    if resultado_cache:
        latencia = time.time() - inicio
        requests.post(URL_METRICAS, json={"evento": "hit", "latencia": latencia})
        print(f"[HIT] consulta {data['id']} servida desde cache")
    else:
        # si no esta en cache pasamos a procesar mediante el generador de resp
        try:
            resp = requests.get(URL_RESPUESTAS, params=params, timeout=5)
            resp.raise_for_status()
            
            # guardar en cache
            r.setex(cache_key, 60, json.dumps(resp.json()))
            latencia = time.time() - inicio
            
            evento = "recovery" if data['retry_count'] > 0 else "miss"
            requests.post(URL_METRICAS, json={"evento": evento, "latencia": latencia})
            print(f"[{evento.upper()}] consulta {data['id']} procesada")

        except requests.exceptions.RequestException as e:
            # MANEJO DE FALLAS 
            data['retry_count'] += 1
            print(f"[FALLA] intento {data['retry_count']} fallido para consulta {data['id']}: {e}")
            
            requests.post(URL_METRICAS, json={"evento": "falla_temporal"})

            if data['retry_count'] >= MAX_RETRIES:
                print(f"[DLQ] consulta {data['id']} excedió los {MAX_RETRIES} intentos. Dead Letter Queue")
                producer.send('dlq_topic', data)
                requests.post(URL_METRICAS, json={"evento": "dlq"})
            else:
                print(f"[RETRY] volviendo a la cola para que la consulta {data['id']} se intente luego nuevamente")
                time.sleep(1) 
                producer.send('reintentos_topic', data)
                requests.post(URL_METRICAS, json={"evento": "retry"})