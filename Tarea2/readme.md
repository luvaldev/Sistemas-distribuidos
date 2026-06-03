# Tarea 2: Procesamiento Asíncrono con Apache Kafka

Este proyecto evoluciona la arquitectura síncrona de la Tarea 1 hacia una arquitectura asíncrona y tolerante a fallos utilizando **Apache Kafka**.

## Requisitos Previos (Entorno Arch Linux / General)
- **Docker** y **Docker Compose** instalados.
- El servicio de Docker debe estar en ejecución (`sudo systemctl start docker`).


## Arquitectura de Componentes (Tarea 2)

### 1. Generador de Trafico (productor kafka)
- **Rol:** Genera rafagas de consultas (uniforme y zipf) simulando el comportamiento de usuarios.
- **Cambio respecto a T1:** Ya no se comunica directamente con la caché de forma bloqueante (HTTP Síncrono). Ahora actúa como un **Producer**, empaquetando cada consulta con un `UUID`, `Timestamp` y un contador de `retry_count`, publicando los mensajes en el tópico principal `consultas_topic`.

