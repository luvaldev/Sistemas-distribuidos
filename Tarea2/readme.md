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