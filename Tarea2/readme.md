# Tarea 2: Procesamiento Asíncrono con Apache Kafka

Este proyecto evoluciona la arquitectura síncrona de la Tarea 1 hacia una arquitectura asíncrona y tolerante a fallos utilizando **Apache Kafka**.

## Requisitos Previos (Entorno Arch Linux / General)
- **Docker** y **Docker Compose** instalados.
- El servicio de Docker debe estar en ejecución (`sudo systemctl start docker`).


## Arquitectura de Componentes (Tarea 2)

### 1. Generador de Trafico (productor kafka)
- **Rol:** Genera rafagas de consultas (uniforme y zipf) simulando el comportamiento de usuarios.
- **Cambio respecto a T1:** Ya no se comunica directamente con la caché de forma bloqueante (HTTP Síncrono). Ahora actúa como un **Producer**, empaquetando cada consulta con un `UUID`, `Timestamp` y un contador de `retry_count`, publicando los mensajes en el tópico principal `consultas_topic`.

### 2. Consumidores Kafka
- **Rol:** Es el procesamiento asíncrono, lee las consultas desde Kafka.
- **Flujo:** Primero verifica si la respuesta esta en Redis (Caché Hit). Si no está, hace una petición al generador de respuestas.
- **Tolerancia a fallos:** Si el generador de Respuestas está caído o se demora demasiado, el consumidor intercepta el error, incrementa el contador de reintentos y envía el mensaje al tópico `reintentos_topic`. Si supera el límite de intentos (3), el mensaje se envía a la `(DLQ)` (`dlq_topic`) para no perder el registro de la consulta fallida.

### 3. Generador de Respuestas y Simulación de Fallas
- **Rol:** Procesa las consultas utilizando el dataset cargado en memoria con Pandas.
- **Simulación de Falla (Caos):** Se implementó un endpoint para simular una caída temporal del servicio y evaluar el comportamiento de los reintentos en Kafka. 

### 4. Sistema de Métricas
- **Rol:** Recopila datos del rendimiento de la arquitectura asíncrona para su posterior análisis.
- **Métricas Registradas:** Throughput, Latencia (p50 y p95), Recoveries (consultas salvadas tras fallos), Retries y eventos de pérdida total (DLQ).

---

### Instrucciones de ejecución (Entorno Arch Linux)

Para ejecutar este sistema distribuido, asegúrate de tener **Docker** y **Docker Compose** instalados en tu distribución.

#### 1. Preparación del Entorno
Asegúrate de que el demonio de Docker esté activo en tu sistema:
```bash
sudo systemctl start docker
```

Para levantar todos los servicios de la Tarea 2 (Kafka, Redis, Consumidores, Métricas y Generador de Tráfico) en segundo plano, ejecútalos desde la carpeta raíz del proyecto:
```bash
cd Tarea2
sudo docker-compose up --build -d
```
#### 2. Monitoreo y Simulación de Fallas
- Ver logs del consumidor (en tiempo real):
```bash
sudo docker-compose logs -f consumidor
```
- Provocar falla temporal
```bash
curl -X POST http://localhost:5001/toggle-falla
```
> Con el mismo comando para desactivar las fallas

#### 3. Resultados y metricas
- Este apartado lo podremos ver en `http://localhost:5002/resumen`
