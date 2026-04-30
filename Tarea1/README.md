# Tarea 1: Plataforma de Análisis de Datos Geoespaciales (Sistemas Distribuidos)

Este proyecto implementa una arquitectura distribuida basada en contenedores para optimizar la consulta de datos geoespaciales sobre edificaciones en Santiago de Chile, utilizando Redis como sistema de caché y simulando tráfico con distribuciones Uniforme y Ley de Zipf.

## Requisitos Previos
Para ejecutar este proyecto necesitas tener instalado en tu sistema:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* [Python](https://www.python.org/downloads/)

## Preparación de los Datos (Importante)
El sistema requiere el dataset de edificios para funcionar. 
1. Descarga el archivo `santiago_buildings.csv` (dataset de Google Open Buildings).
2. Coloca este archivo dentro de la carpeta `respuestas/` antes de construir los contenedores.

## Instrucciones de Despliegue

1. Clona este repositorio en tu computador (con linux).
2. En una terminal en la carpeta raíz del proyecto (donde se encuentra el archivo `docker-compose.yml`).
3. Construye y levanta la infraestructura ejecutando el siguiente comando:
```bash
docker-compose up --build
```

## Ejecución y Monitoreo

Una vez levantado el sistema:

- El contenedor generador-trafico esperará 45 segundos para que los datos pesados se carguen en memoria, y luego enviará automáticamente 2000 consultas (Uniforme y Zipf).
- El contenedor redis-cache interceptará las peticiones aplicando políticas configurables (LRU/LFU).
- Para ver el resumen de los resultados empíricos (Hits, Misses y Latencias), abre un navegador y visita: http://localhost:5002/resumen

> Considerar que para cambiar los tamaños de 50mb 200mb y 500mb hay que hacer las modificaciones en el `docker-compose.yml` en la linea de comando, tambien cambiar LRU o LFU. 

## Detención

Para detener el sistema y limpiar la memoria caché de las pruebas, ejecuta:
```Bash
docker-compose down
```