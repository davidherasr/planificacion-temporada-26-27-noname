# Heras MatchLab | Motor de planificación Noname

Aplicación Streamlit para planificación deportiva, scouting, modelo de juego, presión según rival y construcción de XI ideal.

## Requisitos

```txt
streamlit
pandas
```

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Desplegar en Streamlit Cloud

- Repositorio en GitHub.
- Main file path: `streamlit_app.py`.
- El archivo `requirements.txt` debe estar en la raíz.

## Qué incluye

- Modo claro por defecto y modo oscuro opcional.
- Motor de score por encaje en modelo.
- Modelo Noname: 4-2-3-1 interpretado como 4-4-2, alternativa 3-4-3.
- Scouting con filtros y modo similitud.
- Comparador jugador propio vs recambios.
- Motor de presión según salida rival: 4+1, 4+2, salida de 3, lateral bajo.
- XI ideal sobre campo.
- Informes descargables.
- Exportación CSV.