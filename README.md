<h2> Sistemas Distribuidos </h2> 

En este repositorio documentó la evolución de una arquitectura de software para el procesamiento de datos geoespaciales (Google Open Buildings). El proyecto muestra la transición desde un sistema **síncrono basado en caché** hacia una arquitectura **asíncrona orientada a eventos** y tolerante a fallos.

---

### :wrench: Tecnologías y Herramientas:

<p>
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,docker,redis,kafka"/>
    <br><br>
    <img src="https://skillicons.dev/icons?i=linux,arch,bash,git,github"/>
  </a>
</p>

---

### 📂 Estructura del Repositorio:

<table>
  <tbody>
    <tr valign="top">
      <td width="50%" align="center">
        <h3><a href="./Tarea1">📦 Tarea 1: Arquitectura Síncrona</a></h3>
        <p align="left">
          Implementación inicial de microservicios comunicados vía HTTP (API REST). Se introdujo <b>Redis</b> como sistema de caché en memoria (política LRU/LFU) para mitigar cuellos de botella y reducir la latencia bajo patrones de tráfico Uniforme y Zipf.
        </p>
        <img height="48px" src="https://skillicons.dev/icons?i=redis">
      </td>
      <td width="50%" align="center">
        <h3><a href="./Tarea2">📨 Tarea 2: Procesamiento Asíncrono</a></h3>
        <p align="left">
          Evolución del sistema hacia una arquitectura orientada a eventos utilizando <b>Apache Kafka</b>. Se eliminó el acoplamiento HTTP en favor del patrón Productor/Consumidor, implementando <i>Dead Letter Queues (DLQ)</i> y reintentos para lograr tolerancia a fallos ante caídas del servidor.
        </p>
        <img height="48px" src="https://skillicons.dev/icons?i=kafka">
      </td>
    </tr>
  </tbody>
</table>

---

### Cómo ejecutar los proyectos

Cada tarea está contenida en su propio entorno y cuenta con su respectiva documentación detallada. Para ejecutar cualquiera de las versiones:

1. Clona este repositorio: `git clone https://github.com/luvaldev/Sistemas-distribuidos.git`
2. Navega hacia la carpeta deseada (ej. `cd Tarea2`)
3. Sigue las instrucciones del `README.md` interno de cada carpeta para levantar los servicios usando `docker-compose`.

---
