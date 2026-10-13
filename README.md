# Prueba de concepto: Análisis de código con IA en DevSecOps

La prueba de concepto (POC) tiene como objetivo evaluar la integración de modelos de inteligencia artificial en un pipeline DevSecOps para automatizar el análisis de vulnerabilidades de seguridad durante el proceso de revisión e integración de código.

La solución se plantea sobre un escenario simulado de una empresa del sector financiero que desarrolla una aplicación web basada en una arquitectura de microservicios. En este contexto, se busca incorporar controles de seguridad automatizados al flujo de trabajo de desarrollo, permitiendo detectar posibles vulnerabilidades antes de que los cambios sean integrados en la rama principal del repositorio.

La implementación utiliza un modelo de lenguaje especializado en código, ejecutado localmente mediante Ollama, para analizar los cambios introducidos en una Merge Request o conjunto de modificaciones respecto de la rama principal. El análisis se realiza sobre el diff del código, con el objetivo de identificar posibles vulnerabilidades y determinar si los cambios cumplen con los criterios de seguridad definidos.
