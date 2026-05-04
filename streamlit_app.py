import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="ScoutIQ | No Name FC",
    page_icon="⚽",
    layout="wide"
)

# =========================================================
# ESTILO
# =========================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #08111d 0%, #0c1625 100%);
    color: #e5e7eb;
}
section[data-testid="stSidebar"] {
    background: #0b1320;
    border-right: 1px solid #1f2a37;
}
h1, h2, h3, h4 {
    color: #f8fafc !important;
}
[data-testid="stMetric"] {
    background: #101826;
    border: 1px solid #223043;
    border-radius: 14px;
    padding: 12px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #223043;
    border-radius: 12px;
}
.stTextArea textarea, .stTextInput input {
    background-color: #0f172a !important;
    color: white !important;
}
.small-note {
    font-size: 12px;
    color: #93a4b8;
}
.card-box {
    background: #101826;
    border: 1px solid #223043;
    border-radius: 14px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES
# =========================================================

METRICAS = [
    "duelo_defensivo",
    "duelo_aereo",
    "velocidad_defensiva",
    "salida_balon",
    "presion",
    "decision",
    "fiabilidad_fisica",
    "abp",
    "potencial"
]

NOMBRES_METRICAS = {
    "duelo_defensivo": "Duelo defensivo",
    "duelo_aereo": "Juego aéreo",
    "velocidad_defensiva": "Velocidad defensiva",
    "salida_balon": "Salida de balón",
    "presion": "Presión",
    "decision": "Toma de decisión",
    "fiabilidad_fisica": "Fiabilidad física",
    "abp": "ABP",
    "potencial": "Potencial"
}

PRESETS_MODELO = {
    "Presión alta + ritmo alto": {
        "duelo_defensivo": 8,
        "duelo_aereo": 4,
        "velocidad_defensiva": 9,
        "salida_balon": 6,
        "presion": 10,
        "decision": 8,
        "fiabilidad_fisica": 8,
        "abp": 4,
        "potencial": 7
    },
    "Bloque medio + segunda jugada": {
        "duelo_defensivo": 8,
        "duelo_aereo": 9,
        "velocidad_defensiva": 6,
        "salida_balon": 5,
        "presion": 7,
        "decision": 7,
        "fiabilidad_fisica": 8,
        "abp": 9,
        "potencial": 6
    },
    "Dominante con balón": {
        "duelo_defensivo": 6,
        "duelo_aereo": 4,
        "velocidad_defensiva": 7,
        "salida_balon": 10,
        "presion": 8,
        "decision": 10,
        "fiabilidad_fisica": 7,
        "abp": 5,
        "potencial": 8
    },
    "Reactivo y directo": {
        "duelo_defensivo": 9,
        "duelo_aereo": 9,
        "velocidad_defensiva": 7,
        "salida_balon": 4,
        "presion": 5,
        "decision": 7,
        "fiabilidad_fisica": 8,
        "abp": 9,
        "potencial": 6
    },
    "Personalizado": {
        "duelo_defensivo": 7,
        "duelo_aereo": 7,
        "velocidad_defensiva": 7,
        "salida_balon": 7,
        "presion": 7,
        "decision": 7,
        "fiabilidad_fisica": 7,
        "abp": 7,
        "potencial": 7
    }
}

FORMACIONES = {
    "1-4-4-2": [
        ("POR", 50, 89),
        ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
        ("EI", 18, 50), ("MC", 40, 53), ("MC", 60, 53), ("ED", 82, 50),
        ("DC", 42, 22), ("DC", 58, 22)
    ],
    "1-4-3-3": [
        ("POR", 50, 89),
        ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
        ("MC", 30, 50), ("MC", 50, 56), ("MC", 70, 50),
        ("EI", 20, 24), ("DC", 50, 18), ("ED", 80, 24)
    ],
    "1-4-2-3-1": [
        ("POR", 50, 89),
        ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
        ("MCD", 40, 58), ("MCD", 60, 58),
        ("EI", 20, 38), ("MCO", 50, 37), ("ED", 80, 38),
        ("DC", 50, 18)
    ],
    "1-3-5-2": [
        ("POR", 50, 89),
        ("DFC", 30, 75), ("DFC", 50, 78), ("DFC", 70, 75),
        ("CAI", 15, 52), ("MC", 35, 50), ("MC", 50, 58), ("MC", 65, 50), ("CAD", 85, 52),
        ("DC", 42, 22), ("DC", 58, 22)
    ]
}

MAPEO_PUESTOS = {
    "POR": ["POR"],
    "LD": ["LD", "CAD", "DFC"],
    "LI": ["LI", "CAI", "DFC"],
    "DFC": ["DFC"],
    "MCD": ["MCD", "MC", "DFC"],
    "MC": ["MC", "MCD", "MCO"],
    "MCO": ["MCO", "MC", "SD"],
    "ED": ["ED", "EI", "SD", "DC"],
    "EI": ["EI", "ED", "SD", "DC"],
    "DC": ["DC", "SD", "MCO"],
    "CAD": ["CAD", "LD", "ED"],
    "CAI": ["CAI", "LI", "EI"]
}

# =========================================================
# DATOS DE EJEMPLO
# =========================================================

def datos_ejemplo():
    data = [
        # PROPIOS
        {"nombre":"Ángel","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"POR","rol":"Portero titular","edad":27,"minutos":1800,"duelo_defensivo":3,"duelo_aereo":6,"velocidad_defensiva":6,"salida_balon":6.5,"presion":3,"decision":7,"fiabilidad_fisica":8.2,"abp":6,"potencial":6.5,"confianza":"Alta","estado":"Continuidad","drivers":"fiabilidad, experiencia","observacion":"Portero titular fiable y competitivo. Perfil estable para dar continuidad."},
        {"nombre":"David","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"POR","rol":"Portero suplente","edad":23,"minutos":450,"duelo_defensivo":3,"duelo_aereo":6,"velocidad_defensiva":6.5,"salida_balon":6,"presion":3,"decision":6.2,"fiabilidad_fisica":7.8,"abp":6,"potencial":7.0,"confianza":"Media","estado":"Rotación","drivers":"juventud, margen","observacion":"Suplente con margen, menos asentado pero con capacidad de crecimiento."},

        {"nombre":"Medu","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"LD","rol":"Lateral derecho","edad":26,"minutos":1200,"duelo_defensivo":7.3,"duelo_aereo":6.2,"velocidad_defensiva":7.2,"salida_balon":6.3,"presion":7.5,"decision":6.4,"fiabilidad_fisica":5.8,"abp":5.2,"potencial":6.8,"confianza":"Media","estado":"Duda","drivers":"agresividad, ritmo","observacion":"Lateral competitivo y útil para ritmos altos, condicionado por la fiabilidad física."},
        {"nombre":"Ángel Santiago","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"LD","rol":"Lateral derecho de rotación","edad":22,"minutos":500,"duelo_defensivo":6.8,"duelo_aereo":5.8,"velocidad_defensiva":7.0,"salida_balon":5.9,"presion":7.2,"decision":6.0,"fiabilidad_fisica":7.4,"abp":4.8,"potencial":7.1,"confianza":"Media","estado":"Rotación","drivers":"energía, recorrido","observacion":"Recurso útil para rotación. Más intensidad que precisión."},
        {"nombre":"Raúl Crespo","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"LI","rol":"Lateral izquierdo","edad":25,"minutos":1550,"duelo_defensivo":7.2,"duelo_aereo":6.1,"velocidad_defensiva":6.8,"salida_balon":6.9,"presion":7.0,"decision":6.7,"fiabilidad_fisica":7.8,"abp":7.0,"potencial":6.9,"confianza":"Alta","estado":"Continuidad","drivers":"pierna izquierda, balón parado","observacion":"Lateral útil por perfil zurdo y capacidad para dar salida y ABP."},

        {"nombre":"Amine","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"DFC","rol":"Central dominante","edad":24,"minutos":1450,"duelo_defensivo":8.3,"duelo_aereo":8.9,"velocidad_defensiva":6.4,"salida_balon":5.8,"presion":6.5,"decision":6.8,"fiabilidad_fisica":8.0,"abp":8.9,"potencial":7.4,"confianza":"Alta","estado":"Continuidad","drivers":"duelos, área, ABP","observacion":"Central dominante en área, fuerte en duelos y muy útil en balón parado."},
        {"nombre":"Asiel","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"DFC","rol":"Central corrector","edad":25,"minutos":1600,"duelo_defensivo":8.1,"duelo_aereo":8.2,"velocidad_defensiva":6.6,"salida_balon":6.1,"presion":6.4,"decision":7.1,"fiabilidad_fisica":8.3,"abp":8.4,"potencial":7.1,"confianza":"Alta","estado":"Continuidad","drivers":"regularidad, lectura","observacion":"Central muy fiable y competitivo. Sostiene bien contextos de bloque medio."},
        {"nombre":"Sergi","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"DFC","rol":"Central de apoyo","edad":24,"minutos":900,"duelo_defensivo":7.3,"duelo_aereo":7.2,"velocidad_defensiva":6.9,"salida_balon":6.4,"presion":6.3,"decision":6.7,"fiabilidad_fisica":7.6,"abp":6.7,"potencial":6.9,"confianza":"Media","estado":"Rotación","drivers":"equilibrio, corrección","observacion":"Central equilibrado, útil como complemento y rotación."},

        {"nombre":"Edu","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"MC","rol":"Interior intenso","edad":26,"minutos":1500,"duelo_defensivo":7.6,"duelo_aereo":5.8,"velocidad_defensiva":7.2,"salida_balon":6.4,"presion":8.0,"decision":6.9,"fiabilidad_fisica":8.0,"abp":5.0,"potencial":6.8,"confianza":"Alta","estado":"Continuidad","drivers":"intensidad, presión","observacion":"Interior muy útil para sostener ritmo, presión y comportamiento competitivo."},
        {"nombre":"Frade","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"MC","rol":"Mediocentro combativo","edad":25,"minutos":1400,"duelo_defensivo":7.4,"duelo_aereo":5.0,"velocidad_defensiva":6.7,"salida_balon":6.3,"presion":7.6,"decision":6.8,"fiabilidad_fisica":7.9,"abp":5.8,"potencial":6.6,"confianza":"Alta","estado":"Continuidad","drivers":"agresividad, trabajo","observacion":"Jugador útil por agresividad e interpretación competitiva."},
        {"nombre":"Mati","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"MC","rol":"Mediocentro aéreo","edad":27,"minutos":1000,"duelo_defensivo":6.9,"duelo_aereo":7.7,"velocidad_defensiva":6.2,"salida_balon":6.1,"presion":6.8,"decision":6.5,"fiabilidad_fisica":7.5,"abp":7.3,"potencial":6.5,"confianza":"Media","estado":"Rotación","drivers":"juego aéreo, equilibrio","observacion":"Más útil en contextos físicos y de segunda jugada que en ritmos altos con balón."},
        {"nombre":"Nico","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"MCO","rol":"Mediapunta","edad":22,"minutos":1100,"duelo_defensivo":5.8,"duelo_aereo":5.4,"velocidad_defensiva":6.8,"salida_balon":6.9,"presion":6.7,"decision":7.2,"fiabilidad_fisica":7.6,"abp":5.9,"potencial":7.5,"confianza":"Media","estado":"Duda","drivers":"último pase, llegada","observacion":"Mediapunta interesante para dar más continuidad ofensiva y llegada."},

        {"nombre":"Sergio García","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"ED","rol":"Extremo derecho","edad":24,"minutos":1000,"duelo_defensivo":5.9,"duelo_aereo":5.0,"velocidad_defensiva":6.9,"salida_balon":6.5,"presion":7.0,"decision":6.7,"fiabilidad_fisica":7.3,"abp":6.8,"potencial":6.8,"confianza":"Media","estado":"Rotación","drivers":"centro, golpeo","observacion":"Extremo útil por golpeo y trabajo, más ordenado que desequilibrante."},
        {"nombre":"Raúl Calvo","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"EI","rol":"Extremo izquierdo","edad":24,"minutos":950,"duelo_defensivo":5.7,"duelo_aereo":4.8,"velocidad_defensiva":7.1,"salida_balon":6.7,"presion":6.9,"decision":6.6,"fiabilidad_fisica":7.0,"abp":7.2,"potencial":6.9,"confianza":"Media","estado":"Rotación","drivers":"pierna izquierda, golpeo","observacion":"Extremo zurdo útil para dar amplitud, golpeo y ABP."},
        {"nombre":"Viti","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"ED","rol":"Delantero/extremo de presión","edad":23,"minutos":800,"duelo_defensivo":6.2,"duelo_aereo":5.0,"velocidad_defensiva":7.5,"salida_balon":5.8,"presion":8.1,"decision":5.9,"fiabilidad_fisica":7.5,"abp":5.3,"potencial":7.4,"confianza":"Media","estado":"Duda","drivers":"presión, energía","observacion":"Muy útil para modelos intensos. Menos peso como finalizador o referencia."},

        {"nombre":"Martín","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"DC","rol":"Delantero de apoyo","edad":24,"minutos":700,"duelo_defensivo":5.5,"duelo_aereo":7.0,"velocidad_defensiva":6.1,"salida_balon":5.9,"presion":6.0,"decision":6.2,"fiabilidad_fisica":7.2,"abp":6.8,"potencial":6.6,"confianza":"Media","estado":"Rotación","drivers":"apoyo, remate","observacion":"Perfil de apoyo para alternancia, sin ser un diferencial claro."},
        {"nombre":"Samate","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"DC","rol":"Delantero referencia","edad":27,"minutos":1300,"duelo_defensivo":5.8,"duelo_aereo":8.8,"velocidad_defensiva":6.1,"salida_balon":5.4,"presion":6.2,"decision":6.2,"fiabilidad_fisica":7.0,"abp":9.0,"potencial":6.8,"confianza":"Alta","estado":"Continuidad","drivers":"juego directo, área, ABP","observacion":"Muy útil si el equipo quiere tener referencia, remate y segunda jugada."},
        {"nombre":"Noel","equipo":"No Name FC","tipo":"Propio","liga":"Primera Regional","posicion":"DC","rol":"Delantero rematador","edad":24,"minutos":650,"duelo_defensivo":5.6,"duelo_aereo":8.4,"velocidad_defensiva":6.4,"salida_balon":5.5,"presion":6.3,"decision":6.5,"fiabilidad_fisica":7.4,"abp":8.7,"potencial":7.0,"confianza":"Media","estado":"Revulsivo","drivers":"remate, área","observacion":"Gran amenaza aérea y de remate. Muy interesante como recurso de impacto."},

        # MERCADO
        {"nombre":"Pablo Rivas","equipo":"Ciudad Rodrigo","tipo":"Mercado","liga":"Primera Regional","posicion":"POR","rol":"Portero fiable","edad":25,"minutos":1800,"duelo_defensivo":3,"duelo_aereo":6.2,"velocidad_defensiva":6.3,"salida_balon":6.9,"presion":3,"decision":7.3,"fiabilidad_fisica":8.4,"abp":6.1,"potencial":7.0,"confianza":"Alta","estado":"Objetivo","drivers":"fiabilidad, salida","observacion":"Portero fiable, con buen equilibrio entre seguridad y juego con balón."},
        {"nombre":"Álex Vera","equipo":"Rival 1","tipo":"Mercado","liga":"Primera Regional","posicion":"LD","rol":"Lateral profundo","edad":22,"minutos":1650,"duelo_defensivo":7.8,"duelo_aereo":6.2,"velocidad_defensiva":8.2,"salida_balon":6.7,"presion":7.9,"decision":6.8,"fiabilidad_fisica":8.2,"abp":5.6,"potencial":8.1,"confianza":"Media","estado":"Objetivo","drivers":"velocidad, presión","observacion":"Muy interesante si se quiere lateral agresivo y capaz de defender campo abierto."},
        {"nombre":"Izan Mena","equipo":"Rival 2","tipo":"Mercado","liga":"Primera Regional","posicion":"LI","rol":"Lateral zurdo","edad":23,"minutos":1500,"duelo_defensivo":7.2,"duelo_aereo":6.3,"velocidad_defensiva":7.3,"salida_balon":7.1,"presion":7.0,"decision":6.9,"fiabilidad_fisica":8.1,"abp":6.8,"potencial":7.7,"confianza":"Media","estado":"Objetivo","drivers":"perfil zurdo, salida","observacion":"Perfil útil para reforzar lado izquierdo con más continuidad."},
        {"nombre":"Diego Llorente","equipo":"Rival 3","tipo":"Mercado","liga":"Primera Regional","posicion":"DFC","rol":"Central móvil","edad":21,"minutos":1200,"duelo_defensivo":7.6,"duelo_aereo":7.8,"velocidad_defensiva":7.5,"salida_balon":7.0,"presion":6.8,"decision":7.0,"fiabilidad_fisica":8.0,"abp":7.1,"potencial":8.4,"confianza":"Media","estado":"Objetivo","drivers":"movilidad, salida","observacion":"Central más preparado para defender metros a la espalda y mejorar la salida."},
        {"nombre":"Mario Casas","equipo":"Rival 4","tipo":"Mercado","liga":"Primera Regional","posicion":"MC","rol":"Mediocentro organizador","edad":26,"minutos":1700,"duelo_defensivo":7.1,"duelo_aereo":6.2,"velocidad_defensiva":6.6,"salida_balon":8.2,"presion":7.0,"decision":8.1,"fiabilidad_fisica":8.2,"abp":6.0,"potencial":7.5,"confianza":"Alta","estado":"Objetivo","drivers":"salida, pausa, criterio","observacion":"Perfil interesante para elevar la calidad de la salida y la toma de decisiones."},
        {"nombre":"Adri Navas","equipo":"Rival 5","tipo":"Mercado","liga":"Primera Regional","posicion":"MCO","rol":"Mediapunta creativo","edad":24,"minutos":1450,"duelo_defensivo":5.7,"duelo_aereo":5.1,"velocidad_defensiva":6.9,"salida_balon":7.4,"presion":6.8,"decision":7.8,"fiabilidad_fisica":7.7,"abp":6.3,"potencial":7.9,"confianza":"Media","estado":"Objetivo","drivers":"último pase, claridad","observacion":"Mediapunta más fino para ordenar y acelerar el último tercio."},
        {"nombre":"Pablo Sanz","equipo":"Rival 6","tipo":"Mercado","liga":"Primera Regional","posicion":"ED","rol":"Extremo vertical","edad":22,"minutos":1550,"duelo_defensivo":5.5,"duelo_aereo":4.8,"velocidad_defensiva":8.0,"salida_balon":6.6,"presion":7.4,"decision":6.7,"fiabilidad_fisica":8.0,"abp":5.8,"potencial":8.1,"confianza":"Media","estado":"Objetivo","drivers":"velocidad, desborde","observacion":"Extremo vertical y agresivo. Da ruptura y amenaza al espacio."},
        {"nombre":"Rubén Gil","equipo":"Rival 7","tipo":"Mercado","liga":"Primera Regional","posicion":"DC","rol":"Delantero mixto","edad":24,"minutos":1500,"duelo_defensivo":6.1,"duelo_aereo":7.8,"velocidad_defensiva":7.1,"salida_balon":6.2,"presion":7.4,"decision":6.9,"fiabilidad_fisica":8.3,"abp":7.8,"potencial":7.8,"confianza":"Media","estado":"Objetivo","drivers":"presión, área, movilidad","observacion":"Puede ser muy buen recambio si se busca mezclar presión y amenaza de área."}
    ]
    return pd.DataFrame(data)

# =========================================================
# UTILIDADES
# =========================================================

def normalizar_df(df):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    requeridas = [
        "nombre", "equipo", "tipo", "liga", "posicion", "rol",
        "edad", "minutos"
    ] + METRICAS

    faltan = [c for c in requeridas if c not in df.columns]

    if faltan:
        return None, faltan

    opcionales = {
        "confianza": "Media",
        "estado": "Pendiente",
        "drivers": "",
        "observacion": ""
    }

    for col, valor in opcionales.items():
        if col not in df.columns:
            df[col] = valor

    numericas = ["edad", "minutos"] + METRICAS
    for c in numericas:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["tipo"] = df["tipo"].astype(str).str.strip()
    df["posicion"] = df["posicion"].astype(str).str.strip().str.upper()

    return df, []

def score_jugador(row, pesos):
    total = sum(pesos.values())
    if total == 0:
        return 0.0
    valor = sum(float(row[m]) * pesos[m] for m in METRICAS) / total
    return round(valor, 2)

def nivel_score(score):
    if score >= 8.25:
        return "Muy alto"
    elif score >= 7.25:
        return "Alto"
    elif score >= 6.25:
        return "Medio"
    else:
        return "Bajo"

def semaforo(score):
    if score >= 8.25:
        return "🟢"
    elif score >= 7.25:
        return "🟡"
    elif score >= 6.25:
        return "🟠"
    else:
        return "🔴"

def bonus_slot(posicion, slot):
    candidatos = MAPEO_PUESTOS.get(slot, [])
    if not candidatos:
        return 0
    if posicion == slot:
        return 0.35
    elif posicion in candidatos:
        return 0.15
    return 0

def top_metricas_modelo(pesos):
    orden = sorted(pesos.items(), key=lambda x: x[1], reverse=True)
    top = [NOMBRES_METRICAS[k] for k, _ in orden[:3]]
    bottom = [NOMBRES_METRICAS[k] for k, _ in orden[-2:]]
    return top, bottom

def texto_modelo(pesos):
    top, bottom = top_metricas_modelo(pesos)
    return (
        f"El modelo actual prioriza especialmente **{top[0]}**, **{top[1]}** y **{top[2]}**. "
        f"En cambio, da menos peso relativo a **{bottom[0]}** y **{bottom[1]}**. "
        f"Por tanto, el ranking no mide solo calidad individual, sino compatibilidad con la idea de juego."
    )

def similitud_jugador(row, ref, pesos):
    total = sum(pesos.values())
    if total == 0:
        total = 1
    distancia = sum((((float(row[m]) - float(ref[m])) ** 2) * pesos[m]) for m in METRICAS) / total
    distancia = distancia ** 0.5
    similitud = max(0, 10 - (distancia * 1.8))
    return round(similitud, 2)

def construir_xi(pool, formacion):
    disposicion = FORMACIONES[formacion]
    seleccionados = []
    usados = set()

    for slot, x, y in disposicion:
        candidatos = pool[
            (~pool["nombre"].isin(usados)) &
            (pool["posicion"].isin(MAPEO_PUESTOS.get(slot, [slot])))
        ].copy()

        if candidatos.empty:
            seleccionados.append({
                "slot": slot,
                "x": x,
                "y": y,
                "nombre": "Vacante",
                "equipo": "",
                "posicion": slot,
                "score_modelo": 0,
                "vacante": True
            })
            continue

        candidatos["slot_bonus"] = candidatos["posicion"].apply(lambda p: bonus_slot(p, slot))
        candidatos["score_slot"] = candidatos["score_modelo"] + candidatos["slot_bonus"]

        mejor = candidatos.sort_values(
            ["score_slot", "score_modelo", "minutos"],
            ascending=False
        ).iloc[0]

        usados.add(mejor["nombre"])
        seleccionados.append({
            "slot": slot,
            "x": x,
            "y": y,
            "nombre": mejor["nombre"],
            "equipo": mejor["equipo"],
            "posicion": mejor["posicion"],
            "score_modelo": mejor["score_modelo"],
            "vacante": False
        })

    banquillo = pool[~pool["nombre"].isin(usados)].sort_values(
        ["score_modelo", "minutos"], ascending=False
    ).head(7)

    return seleccionados, banquillo

def renderizar_campo(xi):
    html = []
    html.append("""
    <div style="position:relative;width:100%;height:640px;background:#27ae35;border:4px solid #d5f5d9;border-radius:18px;overflow:hidden;">
        <div style="position:absolute;left:50%;top:0;bottom:0;width:2px;background:rgba(255,255,255,0.55);transform:translateX(-1px);"></div>
        <div style="position:absolute;left:50%;top:50%;width:110px;height:110px;border:2px solid rgba(255,255,255,0.55);border-radius:50%;transform:translate(-55px,-55px);"></div>
        <div style="position:absolute;left:0;right:0;top:0;height:2px;background:rgba(255,255,255,0.55);"></div>
        <div style="position:absolute;left:0;right:0;bottom:0;height:2px;background:rgba(255,255,255,0.55);"></div>
        <div style="position:absolute;top:12%;left:22%;right:22%;height:16%;border:2px solid rgba(255,255,255,0.55);"></div>
        <div style="position:absolute;bottom:12%;left:22%;right:22%;height:16%;border:2px solid rgba(255,255,255,0.55);"></div>
        <div style="position:absolute;top:12%;left:35%;right:35%;height:7%;border:2px solid rgba(255,255,255,0.55);"></div>
        <div style="position:absolute;bottom:12%;left:35%;right:35%;height:7%;border:2px solid rgba(255,255,255,0.55);"></div>
    """)

    for p in xi:
        left = p["x"]
        top = p["y"]

        if p["vacante"]:
            bg = "#374151"
            borde = "#9ca3af"
            texto = "Vacante"
            sub = p["slot"]
            score = "--"
        else:
            bg = "#0b1020"
            borde = "#60a5fa"
            texto = p["nombre"]
            sub = f"{p['slot']} · {p['equipo']}"
            score = f"{p['score_modelo']:.1f}"

        card = f"""
        <div style="
            position:absolute;
            left:calc({left}% - 68px);
            top:calc({top}% - 36px);
            width:136px;
            min-height:72px;
            background:{bg};
            color:white;
            border:2px solid {borde};
            border-radius:12px;
            text-align:center;
            padding:10px 8px 8px 8px;
            box-shadow:0 4px 12px rgba(0,0,0,0.25);
        ">
            <div style="
                position:absolute;
                top:-14px;
                left:50%;
                transform:translateX(-50%);
                background:#2563eb;
                border:2px solid #93c5fd;
                width:34px;
                height:34px;
                line-height:30px;
                border-radius:50%;
                font-size:12px;
                font-weight:700;
            ">{score}</div>
            <div style="font-size:14px;font-weight:700;margin-top:6px;line-height:1.1;">{texto}</div>
            <div style="font-size:11px;color:#fbbf24;margin-top:4px;">{sub}</div>
        </div>
        """
        html.append(card)

    html.append("</div>")
    return "".join(html)

def resumen_necesidades(df_propios):
    if df_propios.empty:
        return "No hay jugadores propios cargados."
    por_pos = df_propios.groupby("posicion")["score_modelo"].mean().sort_values()
    debiles = por_pos.head(3).index.tolist()
    return (
        "Según el modelo actual, las posiciones con menor encaje medio en la plantilla propia son: "
        + ", ".join(debiles) + "."
    )

def informe_jugador(row):
    return f"""
INFORME INDIVIDUAL — {row['nombre']}

Equipo: {row['equipo']}
Tipo: {row['tipo']}
Liga: {row['liga']}
Posición: {row['posicion']}
Rol: {row['rol']}
Edad: {row['edad']}
Minutos: {row['minutos']}
Estado: {row['estado']}
Confianza: {row['confianza']}

Score de encaje en modelo: {row['score_modelo']}/10
Nivel de encaje: {row['nivel']}

Drivers principales:
{row['drivers']}

Observación técnico-táctica:
{row['observacion']}

Conclusión:
{row['nombre']} debe valorarse en relación directa con el modelo de juego, no solo por rendimiento bruto. 
El dato más importante no es si el jugador “es bueno”, sino si ayuda a sostener los comportamientos colectivos que se quieren priorizar.
"""

def informe_plantilla(df_propios, modelo_nombre):
    media = round(df_propios["score_modelo"].mean(), 2) if not df_propios.empty else 0
    top = df_propios.sort_values("score_modelo", ascending=False).head(5)["nombre"].tolist()
    bajos = df_propios.sort_values("score_modelo", ascending=True).head(4)["nombre"].tolist()

    return f"""
RESUMEN EJECUTIVO DE PLANTILLA — NO NAME FC

Fecha: {datetime.now().strftime('%d/%m/%Y')}
Modelo seleccionado: {modelo_nombre}

Número de jugadores propios: {len(df_propios)}
Encaje medio de plantilla: {media}/10

Jugadores con mejor encaje actual:
{", ".join(top) if top else "Sin datos"}

Jugadores con encaje más comprometido:
{", ".join(bajos) if bajos else "Sin datos"}

Lectura general:
La herramienta permite detectar qué perfiles sostienen mejor el modelo competitivo y qué posiciones o jugadores generan más dudas estructurales. 
Esto ayuda a separar continuidad, rotación, duda y necesidad de mercado.
"""

# =========================================================
# INICIALIZACIÓN
# =========================================================

if "players" not in st.session_state:
    st.session_state.players = datos_ejemplo()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("ScoutIQ No Name")
st.sidebar.caption("Inteligencia deportiva y modelo de juego")

archivo = st.sidebar.file_uploader("Subir CSV de jugadores", type=["csv"])

if archivo is not None:
    try:
        temp_df = pd.read_csv(archivo)
        normalizado, faltan = normalizar_df(temp_df)
        if faltan:
            st.sidebar.error("Faltan columnas obligatorias: " + ", ".join(faltan))
        else:
            st.session_state.players = normalizado
            st.sidebar.success("CSV cargado correctamente.")
    except Exception as e:
        st.sidebar.error(f"Error al leer el CSV: {e}")

if st.sidebar.button("Restaurar datos de ejemplo"):
    st.session_state.players = datos_ejemplo()
    st.sidebar.success("Se han restaurado los datos de ejemplo.")

st.sidebar.markdown("---")

modelo = st.sidebar.selectbox(
    "Modelo de juego",
    list(PRESETS_MODELO.keys()),
    index=1
)

st.sidebar.subheader("Pesos del modelo")
pesos = {}
for m in METRICAS:
    pesos[m] = st.sidebar.slider(
        NOMBRES_METRICAS[m],
        0,
        10,
        PRESETS_MODELO[modelo][m]
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div class='small-note'>El CSV debe incluir al menos estas columnas: nombre, equipo, tipo, liga, posicion, rol, edad, minutos y todas las métricas del modelo.</div>",
    unsafe_allow_html=True
)

# =========================================================
# CÁLCULO BASE
# =========================================================

df = st.session_state.players.copy()
df["score_modelo"] = df.apply(lambda row: score_jugador(row, pesos), axis=1)
df["nivel"] = df["score_modelo"].apply(nivel_score)
df["semaforo"] = df["score_modelo"].apply(semaforo)

df_propios = df[df["tipo"] == "Propio"].copy()
df_mercado = df[df["tipo"] == "Mercado"].copy()

# =========================================================
# CABECERA
# =========================================================

st.title("ScoutIQ | No Name FC")
st.caption("Plataforma de scouting, encaje en modelo, planificación de plantilla y construcción de once ideal")

tabs = st.tabs([
    "📊 Dashboard",
    "🔎 Scouting",
    "🔁 Comparador",
    "🧠 Modelo",
    "🧩 Once ideal",
    "📝 Informes"
])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================

with tabs[0]:
    st.header("Dashboard general")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Jugadores cargados", len(df))
    c2.metric("Propios", len(df_propios))
    c3.metric("Mercado", len(df_mercado))
    c4.metric("Encaje medio plantilla", round(df_propios["score_modelo"].mean(), 2) if not df_propios.empty else 0)
    c5.metric("Encaje medio mercado", round(df_mercado["score_modelo"].mean(), 2) if not df_mercado.empty else 0)

    col1, col2 = st.columns([1.15, 1])

    with col1:
        st.subheader("Plantilla propia")
        mostrar = df_propios[[
            "semaforo", "nombre", "posicion", "rol", "edad", "minutos",
            "score_modelo", "nivel", "estado", "drivers"
        ]].sort_values("score_modelo", ascending=False)

        st.dataframe(mostrar, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Encaje medio por posición (plantilla propia)")
        if not df_propios.empty:
            por_pos = df_propios.groupby("posicion")["score_modelo"].mean().sort_values(ascending=False)
            st.bar_chart(por_pos)
        else:
            st.info("No hay datos de plantilla propia.")

        st.subheader("Lectura rápida")
        st.info(resumen_necesidades(df_propios))
        st.write(texto_modelo(pesos))

    st.subheader("Top mercado recomendado por score")
    top_mercado = df_mercado.sort_values("score_modelo", ascending=False).head(8)
    st.dataframe(
        top_mercado[[
            "semaforo", "nombre", "equipo", "posicion", "rol", "edad",
            "score_modelo", "nivel", "confianza", "drivers"
        ]],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# TAB 2 - SCOUTING
# =========================================================

with tabs[1]:
    st.header("Scouting y ranking")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        busqueda = st.text_input("Buscar jugador")
        pos_filter = st.multiselect("Posición", sorted(df["posicion"].unique()), default=sorted(df["posicion"].unique()))
    with f2:
        tipo_filter = st.multiselect("Tipo", sorted(df["tipo"].unique()), default=sorted(df["tipo"].unique()))
        liga_filter = st.multiselect("Liga", sorted(df["liga"].unique()), default=sorted(df["liga"].unique()))
    with f3:
        equipo_filter = st.multiselect("Equipo", sorted(df["equipo"].unique()), default=sorted(df["equipo"].unique()))
        edad_filter = st.slider("Edad", 16, 40, (18, 30))
    with f4:
        score_min = st.slider("Score mínimo", 0.0, 10.0, 6.0, 0.1)
        modo = st.radio("Modo", ["Ranking", "Similitud"], horizontal=True)

    scouting = df[
        (df["posicion"].isin(pos_filter)) &
        (df["tipo"].isin(tipo_filter)) &
        (df["liga"].isin(liga_filter)) &
        (df["equipo"].isin(equipo_filter)) &
        (df["edad"].between(edad_filter[0], edad_filter[1])) &
        (df["score_modelo"] >= score_min)
    ].copy()

    if busqueda:
        scouting = scouting[scouting["nombre"].str.contains(busqueda, case=False, na=False)]

    if modo == "Similitud" and not scouting.empty:
        ref = st.selectbox("Jugador referencia para similitud", df["nombre"].tolist())
        ref_row = df[df["nombre"] == ref].iloc[0]
        mismo_puesto = st.checkbox("Solo misma posición que el jugador referencia", value=True)

        if mismo_puesto:
            scouting = scouting[scouting["posicion"] == ref_row["posicion"]].copy()

        scouting["similitud"] = scouting.apply(lambda row: similitud_jugador(row, ref_row, pesos), axis=1)
        scouting = scouting.sort_values(["similitud", "score_modelo"], ascending=False)

        cols_rank = [
            "semaforo", "nombre", "equipo", "posicion", "edad",
            "score_modelo", "similitud", "nivel", "drivers"
        ]
    else:
        scouting = scouting.sort_values("score_modelo", ascending=False)
        cols_rank = [
            "semaforo", "nombre", "equipo", "posicion", "edad",
            "score_modelo", "nivel", "confianza", "drivers"
        ]

    st.dataframe(scouting[cols_rank], use_container_width=True, hide_index=True)

    st.subheader("Detalle del jugador")
    if not scouting.empty:
        elegido = st.selectbox("Seleccionar jugador para detalle", scouting["nombre"].tolist())
        det = scouting[scouting["nombre"] == elegido].iloc[0]

        c1, c2 = st.columns([1, 1.2])

        with c1:
            st.metric("Score", det["score_modelo"])
            st.metric("Nivel", det["nivel"])
            st.metric("Confianza", det["confianza"])
            st.write(f"**Posición:** {det['posicion']}")
            st.write(f"**Rol:** {det['rol']}")
            st.write(f"**Drivers:** {det['drivers']}")
            st.write(f"**Observación:** {det['observacion']}")

        with c2:
            perfil = pd.DataFrame({
                "Métrica": [NOMBRES_METRICAS[m] for m in METRICAS],
                "Valor": [det[m] for m in METRICAS]
            }).set_index("Métrica")
            st.bar_chart(perfil)
    else:
        st.info("No hay jugadores con esos filtros.")

# =========================================================
# TAB 3 - COMPARADOR
# =========================================================

with tabs[2]:
    st.header("Comparador de jugadores")

    c1, c2, c3 = st.columns([1, 1, 0.8])

    with c1:
        jugador_a = st.selectbox("Jugador A", df["nombre"].tolist(), index=0)
    with c2:
        pos_a = df[df["nombre"] == jugador_a].iloc[0]["posicion"]
        opciones_b = df[df["posicion"] == pos_a]["nombre"].tolist()
        if jugador_a not in opciones_b:
            opciones_b.append(jugador_a)
        jugador_b = st.selectbox("Jugador B", opciones_b, index=min(1, len(opciones_b)-1))
    with c3:
        mismo_tipo = st.checkbox("Comparación cerrada (misma posición)", value=True)

    row_a = df[df["nombre"] == jugador_a].iloc[0]
    row_b = df[df["nombre"] == jugador_b].iloc[0]

    comp = pd.DataFrame({
        "Métrica": [NOMBRES_METRICAS[m] for m in METRICAS],
        row_a["nombre"]: [row_a[m] for m in METRICAS],
        row_b["nombre"]: [row_b[m] for m in METRICAS],
        "Diferencia B-A": [round(row_b[m] - row_a[m], 2) for m in METRICAS]
    })

    top1, top2 = st.columns(2)
    with top1:
        st.markdown("### Jugador A")
        st.write(f"**Nombre:** {row_a['nombre']}")
        st.write(f"**Equipo:** {row_a['equipo']}")
        st.write(f"**Posición:** {row_a['posicion']}")
        st.write(f"**Rol:** {row_a['rol']}")
        st.write(f"**Score:** {row_a['score_modelo']}")
        st.write(f"**Drivers:** {row_a['drivers']}")
    with top2:
        st.markdown("### Jugador B")
        st.write(f"**Nombre:** {row_b['nombre']}")
        st.write(f"**Equipo:** {row_b['equipo']}")
        st.write(f"**Posición:** {row_b['posicion']}")
        st.write(f"**Rol:** {row_b['rol']}")
        st.write(f"**Score:** {row_b['score_modelo']}")
        st.write(f"**Drivers:** {row_b['drivers']}")

    cc1, cc2 = st.columns([1, 1])

    with cc1:
        st.subheader("Tabla comparativa")
        st.dataframe(comp, use_container_width=True, hide_index=True)

    with cc2:
        st.subheader("Comparación visual")
        chart_df = comp.set_index("Métrica")[[row_a["nombre"], row_b["nombre"]]]
        st.bar_chart(chart_df)

    st.subheader("Lectura")
    if row_b["score_modelo"] > row_a["score_modelo"]:
        st.success(f"{row_b['nombre']} mejora el encaje global respecto a {row_a['nombre']} ({row_b['score_modelo']} vs {row_a['score_modelo']}).")
    elif row_b["score_modelo"] < row_a["score_modelo"]:
        st.warning(f"{row_b['nombre']} no mejora el score global frente a {row_a['nombre']}, aunque puede aportar matices concretos.")
    else:
        st.info("Ambos perfiles tienen un encaje global similar. La decisión dependerá del contexto y del rol específico.")

# =========================================================
# TAB 4 - MODELO
# =========================================================

with tabs[3]:
    st.header("Modelo de juego y sensibilidad")

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Pesos actuales")
        pesos_df = pd.DataFrame({
            "Principio": [NOMBRES_METRICAS[m] for m in METRICAS],
            "Peso": [pesos[m] for m in METRICAS]
        }).set_index("Principio")
        st.bar_chart(pesos_df)

    with c2:
        st.subheader("Interpretación")
        top, bottom = top_metricas_modelo(pesos)
        st.write(f"**Modelo seleccionado:** {modelo}")
        st.write(f"**Prioridades altas:** {', '.join(top)}")
        st.write(f"**Prioridades bajas:** {', '.join(bottom)}")
        st.info(texto_modelo(pesos))

    st.subheader("Rendimiento medio por posición según fuente")
    fuente_pos = st.radio("Fuente", ["Propio", "Mercado", "Todos"], horizontal=True)

    if fuente_pos == "Propio":
        base_pos = df_propios.copy()
    elif fuente_pos == "Mercado":
        base_pos = df_mercado.copy()
    else:
        base_pos = df.copy()

    if not base_pos.empty:
        by_pos = base_pos.groupby("posicion")["score_modelo"].mean().sort_values(ascending=False)
        st.bar_chart(by_pos)
    else:
        st.info("Sin datos para esa fuente.")

    st.subheader("Posibles prioridades de mercado")
    if not df_propios.empty:
        media_pos = df_propios.groupby("posicion")["score_modelo"].mean().sort_values()
        bajas = media_pos.head(3).reset_index()
        st.dataframe(bajas.rename(columns={"score_modelo": "encaje_medio"}), use_container_width=True, hide_index=True)
    else:
        st.info("No hay plantilla propia cargada.")

# =========================================================
# TAB 5 - ONCE IDEAL
# =========================================================

with tabs[4]:
    st.header("Once ideal y banquillo recomendado")

    o1, o2, o3 = st.columns([1, 1, 1])

    with o1:
        formacion = st.selectbox("Sistema de juego", list(FORMACIONES.keys()), index=0)
    with o2:
        fuente_once = st.radio("Fuente del XI", ["Solo propios", "Solo mercado", "Mixto"], horizontal=True)
    with o3:
        score_once = st.slider("Score mínimo para considerar", 0.0, 10.0, 0.0, 0.1)

    if fuente_once == "Solo propios":
        pool = df_propios.copy()
    elif fuente_once == "Solo mercado":
        pool = df_mercado.copy()
    else:
        pool = df.copy()

    pool = pool[pool["score_modelo"] >= score_once].copy()
    xi, banquillo = construir_xi(pool, formacion)

    st.markdown(renderizar_campo(xi), unsafe_allow_html=True)

    st.subheader("XI seleccionado")
    xi_df = pd.DataFrame([
        {
            "slot": p["slot"],
            "nombre": p["nombre"],
            "equipo": p["equipo"],
            "posicion_real": p["posicion"],
            "score_modelo": p["score_modelo"]
        }
        for p in xi
    ])
    st.dataframe(xi_df, use_container_width=True, hide_index=True)

    st.subheader("Banquillo recomendado")
    if not banquillo.empty:
        st.dataframe(
            banquillo[[
                "nombre", "equipo", "posicion", "rol", "score_modelo", "nivel", "estado"
            ]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay jugadores disponibles para banquillo.")

    vacantes = [p for p in xi if p["vacante"]]
    if vacantes:
        slots_vacios = ", ".join([v["slot"] for v in vacantes])
        st.warning(f"El sistema detecta vacantes o falta de perfiles adecuados para estos slots: {slots_vacios}.")
    else:
        st.success("Se ha podido construir un XI completo con la base seleccionada.")

# =========================================================
# TAB 6 - INFORMES
# =========================================================

with tabs[5]:
    st.header("Informes y exportación")

    sub1, sub2 = st.tabs(["📄 Informe jugador", "📑 Resumen plantilla"])

    with sub1:
        elegido_inf = st.selectbox("Seleccionar jugador para informe", df["nombre"].tolist())
        row_inf = df[df["nombre"] == elegido_inf].iloc[0]
        texto_inf = informe_jugador(row_inf)

        st.text_area("Informe generado", texto_inf, height=380)
        st.download_button(
            "Descargar informe TXT",
            data=texto_inf,
            file_name=f"informe_{row_inf['nombre'].replace(' ', '_')}.txt",
            mime="text/plain"
        )

    with sub2:
        resumen = informe_plantilla(df_propios, modelo)
        st.text_area("Resumen ejecutivo de plantilla", resumen, height=300)

        exp1, exp2, exp3 = st.columns(3)

        with exp1:
            st.download_button(
                "Exportar ranking CSV",
                data=df.sort_values("score_modelo", ascending=False).to_csv(index=False).encode("utf-8"),
                file_name=f"ranking_noname_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        with exp2:
            st.download_button(
                "Exportar XI CSV",
                data=xi_df.to_csv(index=False).encode("utf-8"),
                file_name=f"xi_ideal_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        with exp3:
            st.download_button(
                "Descargar resumen TXT",
                data=resumen,
                file_name=f"resumen_plantilla_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )