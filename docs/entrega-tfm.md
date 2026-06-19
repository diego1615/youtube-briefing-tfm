# Checklist de entrega TFM

Documento de control para completar el formulario final del master.

## Recursos del proyecto

| Requisito | Estado | Ubicacion |
| --- | --- | --- |
| Documentacion completa | Listo | `README.md` |
| Codigo fuente | Listo | Repositorio GitHub publico |
| Repositorio GitHub | Preparado | `https://github.com/diego1615/youtube-briefing-tfm` |
| Despliegue | Pendiente | Completar URL despues de Streamlit Cloud |
| Slides | Listo | https://docs.google.com/presentation/d/1lYlGqyycLlqZ9CUEBBYMQoiovi4FByi_Wa1CkFtQew4 compartido con `mouredev@gmail.com` |
| Video explicativo | Pendiente de grabar | Usar `docs/video-guia.md` |
| Usuario/contrasena de prueba | No aplica | La app no tiene login |
| IA generativa | Listo local | Briefing con modelos locales de Ollama |
| Reproduccion embebida | Listo | Toggle `Reproducir en la app` en resultados de noticias |
| Matriz de consigna | Listo | `docs/consigna-checklist.md` |

## Datos para el formulario

- Nombre completo del alumno: completar en el formulario.
- Email utilizado en la inscripcion: completar en el formulario, no publicarlo en el repo.
- URL del repositorio de GitHub: `https://github.com/diego1615/youtube-briefing-tfm`
- URL de despliegue: pendiente.
- URL de slides: `https://docs.google.com/presentation/d/1lYlGqyycLlqZ9CUEBBYMQoiovi4FByi_Wa1CkFtQew4`
- URL del video: pendiente.
- Usuario y contrasena de prueba: no aplica.
- Nota de IA generativa: la demo local usa Ollama; en despliegue cloud puede quedar desactivada con `OLLAMA_ENABLED=false`.
- Nota de reproduccion: los resultados de noticias permiten abrir el video dentro de la app con `Reproducir en la app`.

## Antes de enviar

- [x] Confirmar que el repositorio es publico.
- [x] Confirmar que `.env` no fue subido.
- [ ] Confirmar que la app publicada tiene configurado `YOUTUBE_API_KEY` como secret.
- [ ] En demo local, confirmar que Ollama esta activo antes de grabar el video.
- [ ] En demo local, mostrar el toggle `Reproducir en la app` en un resultado.
- [ ] Pegar la URL real de despliegue en `README.md` y en este archivo.
- [ ] Subir/grabar el video explicativo con captura de pantalla.
- [ ] Pegar la URL publica del video en el formulario.
- [x] Confirmar que las slides estan enlazadas desde el repo y compartidas con `mouredev@gmail.com`.
