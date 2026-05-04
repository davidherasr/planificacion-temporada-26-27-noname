import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Heras MatchLab | Noname",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS - modo claro por defecto, con opción oscura
# =========================================================

def aplicar_estilo(modo_visual: str):
    if modo_visual == "Oscuro":
        st.markdown("""
        <style>
        .stApp {background:#0b1118;color:#e5e7eb;}
        section[data-testid="stSidebar"] {background:#101923;border-right:1px solid #263241;}
        h1,h2,h3,h4 {color:#f8fafc !important;}
        [data-testid="stMetric"] {background:#111827;border:1px solid #263241;padding:14px;border-radius:14px;}
        .card {background:#111827;border:1px solid #263241;border-radius:14px;padding:14px;margin-bottom:10px;}
        .soft {color:#9ca3af;}
        .tag {display:inline-block;background:#1e293b;color:#dbeafe;border:1px solid #334155;border-radius:999px;padding:4px 10px;margin:2px;font-size:12px;}
        .danger {background:#3b1111;border:1px solid #7f1d1d;}
        .ok {background:#0f2f22;border:1px solid #166534;}
        .warn {background:#312811;border:1px solid #854d0e;}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {background:#f7f9fc;color:#111827;}
        section[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #e5e7eb;}
        h1,h2,h3,h4 {color:#0f172a !important;}
        [data-testid="stMetric"] {background:#ffffff;border:1px solid #e5e7eb;padding:14px;border-radius:14px;box-shadow:0 1px 3px rgba(15,23,42,0.06);}
        .card {background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;padding:14px;margin-bottom:10px;box-shadow:0 1px 3px rgba(15,23,42,0.06);}
        .soft {color:#64748b;}
        .tag {display:inline-block;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:999px;padding:4px 10px;margin:2px;font-size:12px;}
        .danger {background:#fff1f2;border:1px solid #fecdd3;}
        .ok {background:#ecfdf5;border:1px solid #bbf7d0;}
        .warn {background:#fffbeb;border:1px solid #fde68a;}
        </style>
        """, unsafe_allow_html=True)

# =========================================================
# MÉTRICAS, MODELOS Y FORMACIONES
# =========================================================

METRICAS = [
    "duelo_defensivo", "duelo_aereo", "velocidad_defensiva", "salida_balon",
    "presion", "decision", "fiabilidad_fisica", "abp", "potencial",
    "asociacion", "ruptura", "centro_lateral"
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
    "potencial": "Potencial",
    "asociacion": "Asociación",
    "ruptura": "Ruptura",
    "centro_lateral": "Centro lateral"
}

MODELO_NONAME = {
    "sistema_nominal": "4-2-3-1",
    "estructura_real": "4-4-2 con mediapunta como segundo punta libre",
    "sistema_alternativo": "3-4-3 con carriles altos y cuadrado interior",
    "identidad": "Equipo con organización posicional de base, vertical cuando roba o encuentra ventaja.",
    "salida": "Salida de cuatro del 4-2-3-1. Laterales asimétricos: uno largo y otro corto/interior a altura de centrales.",
    "amplitud": "Dos extremos dan amplitud. Si uno se mete dentro, el otro debe permanecer abierto.",
    "presion": "Bloque alto. La presión la inician delantero y mediapunta.",
    "orientacion": "Cerrar carril interior para forzar al rival a jugar por fuera.",
    "transicion_ofensiva": "Rápida. Buscar mediapunta libre, delantero o espacio según contexto.",
    "transicion_defensiva": "Presión tras pérdida. Si se supera, embudo interior y reorganización.",
    "rest_defence": "3 defensas + 2 pivotes, o 3 defensas + 1 pivote según altura del segundo pivote.",
    "area": "Ocupación de primer palo, punto de penalti, segundo palo y rechace."
}

PRESETS_MODELO = {
    "Noname base: 4-2-3-1 / 4-4-2 presión alta": {
        "duelo_defensivo": 8, "duelo_aereo": 7, "velocidad_defensiva": 8,
        "salida_balon": 7, "presion": 10, "decision": 9, "fiabilidad_fisica": 8,
        "abp": 7, "potencial": 7, "asociacion": 8, "ruptura": 8, "centro_lateral": 8
    },
    "Noname alternativo: 3-4-3 cuadrado interior": {
        "duelo_defensivo": 7, "duelo_aereo": 7, "velocidad_defensiva": 8,
        "salida_balon": 8, "presion": 9, "decision": 9, "fiabilidad_fisica": 8,
        "abp": 7, "potencial": 7, "asociacion": 9, "ruptura": 7, "centro_lateral": 9
    },
    "Bloque medio + segunda jugada": {
        "duelo_defensivo": 9, "duelo_aereo": 10, "velocidad_defensiva": 6,
        "salida_balon": 5, "presion": 7, "decision": 7, "fiabilidad_fisica": 8,
        "abp": 10, "potencial": 6, "asociacion": 6, "ruptura": 6, "centro_lateral": 8
    },
    "Dominante con balón": {
        "duelo_defensivo": 6, "duelo_aereo": 5, "velocidad_defensiva": 7,
        "salida_balon": 10, "presion": 8, "decision": 10, "fiabilidad_fisica": 7,
        "abp": 5, "potencial": 8, "asociacion": 10, "ruptura": 7, "centro_lateral": 6
    },
    "Personalizado": {
        "duelo_defensivo": 7, "duelo_aereo": 7, "velocidad_defensiva": 7,
        "salida_balon": 7, "presion": 7, "decision": 7, "fiabilidad_fisica": 7,
        "abp": 7, "potencial": 7, "asociacion": 7, "ruptura": 7, "centro_lateral": 7
    }
}

FORMACIONES = {
    "4-2-3-1 Noname": [
        ("POR", 50, 90),
        ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
        ("MCD", 40, 58), ("MC", 60, 58),
        ("EI", 18, 39), ("MCO", 50, 39), ("ED", 82, 39),
        ("DC", 50, 18)
    ],
    "4-4-2 real: MP segundo punta": [
        ("POR", 50, 90),
        ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
        ("EI", 18, 50), ("MCD", 40, 54), ("MC", 60, 54), ("ED", 82, 50),
        ("MCO", 43, 24), ("DC", 57, 19)
    ],
    "3-4-3 cuadrado interior": [
        ("POR", 50, 90),
        ("DFC", 29, 76), ("DFC", 50, 78), ("DFC", 71, 76),
        ("CAI", 15, 54), ("MCD", 40, 56), ("MC", 60, 56), ("CAD", 85, 54),
        ("MCO", 40, 34), ("MCO", 60, 34), ("DC", 50, 18)
    ]
}

MAPEO_PUESTOS = {
    "POR": ["POR"],
    "LD": ["LD", "CAD", "DFC"],
    "LI": ["LI", "CAI", "DFC"],
    "DFC": ["DFC"],
    "MCD": ["MCD", "MC", "DFC"],
    "MC": ["MC", "MCD", "MCO"],
    "MCO": ["MCO", "MC", "DC", "EI", "ED"],
    "ED": ["ED", "EI", "MCO", "DC"],
    "EI": ["EI", "ED", "MCO", "DC"],
    "DC": ["DC", "MCO"],
    "CAD": ["CAD", "LD", "ED"],
    "CAI": ["CAI", "LI", "EI"]
}

REGLAS_PRESION = {
    "Salida de 4 + pivote único": {
        "estructura_rival": "4+1",
        "ajuste": "El delantero va a impares evitando retorno. El mediapunta fija o salta sobre el pivote rival.",
        "salto": "Si el central receptor queda lejos del punta, salta el extremo del lado y la línea defensiva ajusta marcas.",
        "objetivo": "Cerrar dentro, impedir giro del pivote y forzar pase al lateral o balón largo."
    },
    "Salida de 4 + doble pivote": {
        "estructura_rival": "4+2",
        "ajuste": "Delantero y mediapunta van a pares. Uno salta y el otro cierra línea de retorno/interior.",
        "salto": "Extremos orientan hacia fuera y saltan cuando el pase llega al lateral.",
        "objetivo": "Evitar que los dos pivotes reciban de cara y obligar al rival a jugar por fuera."
    },
    "Salida de 3": {
        "estructura_rival": "3+1 / 3+2",
        "ajuste": "Delantero y mediapunta parten desde dentro. Saltan sobre centrales cercanos cuando el balón va al central exterior.",
        "salto": "Si el rival conecta con central alejado, salta el extremo y se realiza cambio de marca en línea defensiva.",
        "objetivo": "Proteger dentro primero, activar presión al exterior y evitar progresión limpia."
    },
    "Lateral bajo en salida": {
        "estructura_rival": "4 que se convierte en 3",
        "ajuste": "Se interpreta igual que una salida de 3 si el lateral baja de forma estable.",
        "salto": "La altura del rival marca la altura de nuestra presión: si ellos bajan, nosotros podemos subir.",
        "objetivo": "No romper la estructura por la altura del lateral: orientar, fijar y saltar cuando el balón viaja fuera."
    }
}

# =========================================================
# DATOS DE EJEMPLO
# =========================================================

def datos_ejemplo():
    data = [
        # Plantilla propia
        ["Ángel", "Noname", "Propio", "Primera Regional", "POR", "Portero titular", 27, 1800, 3, 6, 6, 6.5, 3, 7, 8.2, 6, 6.5, 6, 4, 5, "Alta", "Continuidad", "fiabilidad, experiencia", "Portero titular fiable. Prioridad: seguridad y continuidad."],
        ["David", "Noname", "Propio", "Primera Regional", "POR", "Portero suplente", 23, 450, 3, 6, 6.5, 6, 3, 6.2, 7.8, 6, 7, 6, 4, 5, "Media", "Rotación", "juventud, margen", "Portero con margen y rol de rotación."],
        ["Medu", "Noname", "Propio", "Primera Regional", "LD", "Lateral largo/corto según lado", 26, 1200, 7.3, 6.2, 7.2, 6.3, 7.5, 6.4, 5.8, 5.2, 6.8, 6.5, 6.8, 7.1, "Media", "Duda", "ritmo, agresividad, recorrido", "Lateral competitivo, condicionado por fiabilidad física."],
        ["Ángel Santiago", "Noname", "Propio", "Primera Regional", "LD", "Lateral de rotación", 22, 500, 6.8, 5.8, 7.0, 5.9, 7.2, 6.0, 7.4, 4.8, 7.1, 5.8, 6.7, 6.2, "Media", "Rotación", "energía, recorrido", "Recurso útil para rotación. Más intensidad que precisión."],
        ["Raúl Crespo", "Noname", "Propio", "Primera Regional", "LI", "Lateral izquierdo", 25, 1550, 7.2, 6.1, 6.8, 6.9, 7.0, 6.7, 7.8, 7.0, 6.9, 6.8, 6.2, 7.5, "Alta", "Continuidad", "zurdo, balón parado, salida", "Lateral útil por perfil zurdo, salida y ABP."],
        ["Amine", "Noname", "Propio", "Primera Regional", "DFC", "Central dominante", 24, 1450, 8.3, 8.9, 6.4, 5.8, 6.5, 6.8, 8.0, 8.9, 7.4, 5.8, 5.6, 4.8, "Alta", "Continuidad", "duelo, área, ABP", "Central dominante en área, fuerte en duelos y balón parado."],
        ["Asiel", "Noname", "Propio", "Primera Regional", "DFC", "Central corrector", 25, 1600, 8.1, 8.2, 6.6, 6.1, 6.4, 7.1, 8.3, 8.4, 7.1, 6.0, 5.8, 4.8, "Alta", "Continuidad", "regularidad, lectura, duelo", "Central fiable y competitivo. Sostiene bien el bloque medio-alto."],
        ["Sergi", "Noname", "Propio", "Primera Regional", "DFC", "Central de apoyo", 24, 900, 7.3, 7.2, 6.9, 6.4, 6.3, 6.7, 7.6, 6.7, 6.9, 6.1, 5.9, 5.0, "Media", "Rotación", "equilibrio, corrección", "Central equilibrado, útil como complemento."],
        ["Edu", "Noname", "Propio", "Primera Regional", "MC", "Pivote/MC de recorrido", 26, 1500, 7.6, 5.8, 7.2, 6.4, 8.0, 6.9, 8.0, 5.0, 6.8, 6.7, 7.2, 5.8, "Alta", "Continuidad", "presión, recorrido, intensidad", "Interior muy útil para sostener ritmo y presión."],
        ["Frade", "Noname", "Propio", "Primera Regional", "MC", "Mediocentro combativo", 25, 1400, 7.4, 5.0, 6.7, 6.3, 7.6, 6.8, 7.9, 5.8, 6.6, 6.5, 6.8, 5.5, "Alta", "Continuidad", "agresividad, trabajo, equilibrio", "Jugador útil por agresividad e interpretación competitiva."],
        ["Mati", "Noname", "Propio", "Primera Regional", "MC", "Mediocentro físico", 27, 1000, 6.9, 7.7, 6.2, 6.1, 6.8, 6.5, 7.5, 7.3, 6.5, 6.0, 5.9, 5.8, "Media", "Rotación", "juego aéreo, segunda jugada", "Más útil en contextos físicos y de segunda jugada."],
        ["Nico", "Noname", "Propio", "Primera Regional", "MCO", "Mediapunta asociativo", 22, 1100, 5.8, 5.4, 6.8, 6.9, 6.7, 7.2, 7.6, 5.9, 7.5, 7.4, 6.8, 6.2, "Media", "Duda", "último pase, apoyo, llegada", "Mediapunta interesante para conectar juego y aparecer libre."],
        ["Sergio García", "Noname", "Propio", "Primera Regional", "ED", "Extremo derecho", 24, 1000, 5.9, 5.0, 6.9, 6.5, 7.0, 6.7, 7.3, 6.8, 6.8, 6.7, 6.9, 7.3, "Media", "Rotación", "centro, golpeo, trabajo", "Extremo útil por golpeo, centro y trabajo sin balón."],
        ["Raúl Calvo", "Noname", "Propio", "Primera Regional", "EI", "Extremo izquierdo", 24, 950, 5.7, 4.8, 7.1, 6.7, 6.9, 6.6, 7.0, 7.2, 6.9, 6.8, 7.0, 7.1, "Media", "Rotación", "zurdo, golpeo, amplitud", "Extremo zurdo útil para amplitud, golpeo y ABP."],
        ["Viti", "Noname", "Propio", "Primera Regional", "ED", "Delantero/extremo de presión", 23, 800, 6.2, 5.0, 7.5, 5.8, 8.1, 5.9, 7.5, 5.3, 7.4, 5.9, 7.6, 5.9, "Media", "Duda", "presión, energía, ruptura", "Muy útil para modelos intensos. Menos peso como referencia."],
        ["Martín", "Noname", "Propio", "Primera Regional", "DC", "Delantero de apoyo", 24, 700, 5.5, 7.0, 6.1, 5.9, 6.0, 6.2, 7.2, 6.8, 6.6, 6.1, 6.0, 5.6, "Media", "Rotación", "apoyo, remate", "Perfil de apoyo para alternancia."],
        ["Samate", "Noname", "Propio", "Primera Regional", "DC", "Delantero referencia", 27, 1300, 5.8, 8.8, 6.1, 5.4, 6.2, 6.2, 7.0, 9.0, 6.8, 5.8, 6.4, 6.3, "Alta", "Continuidad", "juego directo, área, ABP", "Muy útil si el equipo necesita referencia, remate y segunda jugada."],
        ["Noel", "Noname", "Propio", "Primera Regional", "DC", "Delantero rematador", 24, 650, 5.6, 8.4, 6.4, 5.5, 6.3, 6.5, 7.4, 8.7, 7.0, 5.7, 6.3, 6.0, "Media", "Revulsivo", "remate, área, juego aéreo", "Gran amenaza aérea y de remate."],

        # Mercado / rivales
        ["Álex Vera", "Rival 1", "Mercado", "Primera Regional", "LD", "Lateral profundo", 22, 1650, 7.8, 6.2, 8.2, 6.7, 7.9, 6.8, 8.2, 5.6, 8.1, 6.7, 7.8, 7.6, "Media", "Objetivo", "velocidad, presión, recorrido", "Muy interesante si se quiere lateral agresivo y capaz de defender campo abierto."],
        ["Izan Mena", "Rival 2", "Mercado", "Primera Regional", "LI", "Lateral zurdo", 23, 1500, 7.2, 6.3, 7.3, 7.1, 7.0, 6.9, 8.1, 6.8, 7.7, 7.1, 6.8, 7.5, "Media", "Objetivo", "perfil zurdo, salida, centro", "Perfil útil para reforzar lado izquierdo con continuidad."],
        ["Diego Llorente", "Rival 3", "Mercado", "Primera Regional", "DFC", "Central móvil", 21, 1200, 7.6, 7.8, 7.5, 7.0, 6.8, 7.0, 8.0, 7.1, 8.4, 6.5, 6.4, 5.2, "Media", "Objetivo", "movilidad, salida, proyección", "Central más preparado para defender metros a la espalda y mejorar salida."],
        ["Mario Casas", "Rival 4", "Mercado", "Primera Regional", "MC", "Mediocentro organizador", 26, 1700, 7.1, 6.2, 6.6, 8.2, 7.0, 8.1, 8.2, 6.0, 7.5, 8.2, 6.4, 6.1, "Alta", "Objetivo", "salida, pausa, criterio", "Perfil para elevar calidad de salida y toma de decisiones."],
        ["Adri Navas", "Rival 5", "Mercado", "Primera Regional", "MCO", "Mediapunta creativo", 24, 1450, 5.7, 5.1, 6.9, 7.4, 6.8, 7.8, 7.7, 6.3, 7.9, 8.0, 7.2, 6.4, "Media", "Objetivo", "último pase, claridad, apoyo", "Mediapunta más fino para ordenar y acelerar el último tercio."],
        ["Pablo Sanz", "Rival 6", "Mercado", "Primera Regional", "ED", "Extremo vertical", 22, 1550, 5.5, 4.8, 8.0, 6.6, 7.4, 6.7, 8.0, 5.8, 8.1, 6.8, 8.2, 7.1, "Media", "Objetivo", "velocidad, desborde, ruptura", "Extremo vertical y agresivo. Da ruptura y amenaza al espacio."],
        ["Rubén Gil", "Rival 7", "Mercado", "Primera Regional", "DC", "Delantero mixto", 24, 1500, 6.1, 7.8, 7.1, 6.2, 7.4, 6.9, 8.3, 7.8, 7.8, 6.5, 7.2, 6.7, "Media", "Objetivo", "presión, área, movilidad", "Buen recambio si se busca mezclar presión y amenaza de área."],
    ]
    cols = ["nombre", "equipo", "tipo", "liga", "posicion", "rol", "edad", "minutos"] + METRICAS + ["confianza", "estado", "drivers", "observacion"]
    return pd.DataFrame(data, columns=cols)

def datos_rivales_ejemplo():
    return pd.DataFrame([
        ["Rival 4+1", "4-3-3", "Salida de 4 + pivote único", "Bloque medio", "Laterales altos", "Transición vertical", "Presionar central receptor, MP sobre pivote, orientar fuera."],
        ["Rival 4+2", "4-2-3-1", "Salida de 4 + doble pivote", "Bloque medio-alto", "Extremos abiertos", "Ataque por banda", "DC+MP a pares, cerrar doble pivote, saltar con extremo a lateral."],
        ["Rival línea de 3", "3-5-2", "Salida de 3", "Bloque medio", "Carriles altos", "Juego directo + segunda jugada", "Partir desde dentro, saltar a centrales exteriores, cambio de marca si conecta alejado."],
    ], columns=["rival", "sistema", "salida_rival", "bloque", "comportamiento_bandas", "amenaza", "plan_presion"])

# =========================================================
# FUNCIONES DE MOTOR
# =========================================================

def normalizar_df(df):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    requeridas = ["nombre", "equipo", "tipo", "liga", "posicion", "rol", "edad", "minutos"] + METRICAS
    faltan = [c for c in requeridas if c not in df.columns]
    if faltan:
        return None, faltan

    for col in ["confianza", "estado", "drivers", "observacion"]:
        if col not in df.columns:
            df[col] = ""

    for c in ["edad", "minutos"] + METRICAS:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["posicion"] = df["posicion"].astype(str).str.upper().str.strip()
    df["tipo"] = df["tipo"].astype(str).str.strip()
    return df, []

def score_jugador(row, pesos):
    total = sum(pesos.values()) or 1
    return round(sum(float(row[m]) * pesos[m] for m in METRICAS) / total, 2)

def nivel(score):
    if score >= 8.25:
        return "Muy alto"
    if score >= 7.25:
        return "Alto"
    if score >= 6.25:
        return "Medio"
    return "Bajo"

def semaforo(score):
    if score >= 8.25:
        return "🟢"
    if score >= 7.25:
        return "🟡"
    if score >= 6.25:
        return "🟠"
    return "🔴"

def similitud(row, ref, pesos):
    total = sum(pesos.values()) or 1
    distancia = sum(((float(row[m]) - float(ref[m])) ** 2) * pesos[m] for m in METRICAS) / total
    distancia = distancia ** 0.5
    return round(max(0, 10 - distancia * 1.7), 2)

def bonus_slot(pos, slot):
    posibles = MAPEO_PUESTOS.get(slot, [slot])
    if pos == slot:
        return 0.35
    if pos in posibles:
        return 0.15
    return -0.20

def construir_xi(pool, formacion):
    slots = FORMACIONES[formacion]
    usados = set()
    xi = []
    for slot, x, y in slots:
        candidatos = pool[(~pool["nombre"].isin(usados)) & (pool["posicion"].isin(MAPEO_PUESTOS.get(slot, [slot])) )].copy()
        if candidatos.empty:
            xi.append({"slot": slot, "x": x, "y": y, "nombre": "VACANTE", "equipo": "", "posicion": slot, "score_modelo": 0, "rol": "Sin perfil", "vacante": True})
            continue
        candidatos["score_slot"] = candidatos["score_modelo"] + candidatos["posicion"].apply(lambda p: bonus_slot(p, slot))
        pick = candidatos.sort_values(["score_slot", "score_modelo", "minutos"], ascending=False).iloc[0]
        usados.add(pick["nombre"])
        xi.append({"slot": slot, "x": x, "y": y, "nombre": pick["nombre"], "equipo": pick["equipo"], "posicion": pick["posicion"], "score_modelo": pick["score_modelo"], "rol": pick["rol"], "vacante": False})
    banquillo = pool[~pool["nombre"].isin(usados)].sort_values(["score_modelo", "minutos"], ascending=False).head(7)
    return xi, banquillo

def render_pizarra(xi, modo_visual):
    pitch_bg = "#23a236"
    line = "rgba(255,255,255,.62)"
    card_bg = "#ffffff" if modo_visual == "Claro" else "#111827"
    card_color = "#0f172a" if modo_visual == "Claro" else "#ffffff"
    border = "#2563eb"
    html = [f"""
    <div style="position:relative;width:100%;height:660px;background:{pitch_bg};border:4px solid #d5f5d9;border-radius:18px;overflow:hidden;">
      <div style="position:absolute;left:50%;top:0;bottom:0;width:2px;background:{line};"></div>
      <div style="position:absolute;left:50%;top:50%;width:116px;height:116px;border:2px solid {line};border-radius:50%;transform:translate(-58px,-58px);"></div>
      <div style="position:absolute;left:22%;right:22%;top:9%;height:18%;border:2px solid {line};"></div>
      <div style="position:absolute;left:34%;right:34%;top:9%;height:8%;border:2px solid {line};"></div>
      <div style="position:absolute;left:22%;right:22%;bottom:9%;height:18%;border:2px solid {line};"></div>
      <div style="position:absolute;left:34%;right:34%;bottom:9%;height:8%;border:2px solid {line};"></div>
    """]
    for p in xi:
        bg = "#f8fafc" if not p["vacante"] and modo_visual == "Claro" else ("#111827" if not p["vacante"] else "#475569")
        color = "#0f172a" if not p["vacante"] and modo_visual == "Claro" else "#ffffff"
        score = "--" if p["vacante"] else f"{p['score_modelo']:.1f}"
        html.append(f"""
        <div style="position:absolute;left:calc({p['x']}% - 76px);top:calc({p['y']}% - 38px);width:152px;min-height:76px;background:{bg};color:{color};border:2px solid {border};border-radius:14px;text-align:center;padding:11px 7px 8px;box-shadow:0 7px 18px rgba(0,0,0,.25);">
          <div style="position:absolute;top:-16px;left:50%;transform:translateX(-50%);background:#2563eb;color:white;border:2px solid #93c5fd;width:38px;height:38px;line-height:34px;border-radius:50%;font-weight:800;font-size:12px;">{score}</div>
          <div style="font-size:15px;font-weight:800;margin-top:8px;line-height:1.05;">{p['nombre']}</div>
          <div style="font-size:11px;color:#f59e0b;margin-top:4px;">{p['slot']} · {p['posicion']}</div>
          <div style="font-size:10px;color:#64748b;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{p['rol']}</div>
        </div>
        """)
    html.append("</div>")
    return "".join(html)

def top_prioridades(pesos):
    orden = sorted(pesos.items(), key=lambda x: x[1], reverse=True)
    return [NOMBRES_METRICAS[x[0]] for x in orden[:4]], [NOMBRES_METRICAS[x[0]] for x in orden[-3:]]

def diagnostico_modelo(pesos):
    altas, bajas = top_prioridades(pesos)
    return f"El motor prioriza {', '.join(altas)}. Las métricas menos determinantes en este ajuste son {', '.join(bajas)}. El score no mide calidad pura: mide compatibilidad con el plan competitivo definido."

def generar_plan_presion(salida_rival, sistema_rival, bloque_rival):
    regla = REGLAS_PRESION.get(salida_rival, REGLAS_PRESION["Salida de 4 + doble pivote"])
    extra = ""
    if bloque_rival == "Bloque bajo":
        extra = " Como el rival tiende a hundirse, la presión inicial debe servir para instalar al equipo en campo rival y sostener rest-defence."
    elif bloque_rival == "Bloque alto":
        extra = " Si el rival aprieta alto, conviene alternar corto-largo y preparar segunda jugada tras atraer."
    else:
        extra = " La clave será sostener altura, orientar fuera y no romper la estructura interior."
    return f"""
**Sistema rival:** {sistema_rival}  
**Estructura de salida rival:** {regla['estructura_rival']}  

**Ajuste principal:** {regla['ajuste']}  
**Salto previsto:** {regla['salto']}  
**Objetivo de la presión:** {regla['objetivo']}  
{extra}
"""

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

Score de encaje en el modelo: {row['score_modelo']}/10
Nivel: {row['nivel']}

Drivers:
{row['drivers']}

Lectura técnico-táctica:
{row['observacion']}

Conclusión:
{row['nombre']} debe valorarse por su coherencia con el modelo Noname: presión alta, cierre interior, verticalidad tras robo, laterales asimétricos, amplitud exterior y rest-defence preparado.
"""

def informe_modelo():
    return f"""
MODELO DE JUEGO — NONAME

Sistema nominal:
{MODELO_NONAME['sistema_nominal']}

Interpretación real:
{MODELO_NONAME['estructura_real']}

Sistema alternativo:
{MODELO_NONAME['sistema_alternativo']}

Identidad:
{MODELO_NONAME['identidad']}

Salida:
{MODELO_NONAME['salida']}

Amplitud:
{MODELO_NONAME['amplitud']}

Presión:
{MODELO_NONAME['presion']}

Orientación defensiva:
{MODELO_NONAME['orientacion']}

Transición ofensiva:
{MODELO_NONAME['transicion_ofensiva']}

Transición defensiva:
{MODELO_NONAME['transicion_defensiva']}

Rest-defence:
{MODELO_NONAME['rest_defence']}

Ocupación de área:
{MODELO_NONAME['area']}
"""

# =========================================================
# INICIALIZACIÓN
# =========================================================

if "players" not in st.session_state:
    st.session_state.players = datos_ejemplo()
if "rivals" not in st.session_state:
    st.session_state.rivals = datos_rivales_ejemplo()

# =========================================================
# SIDEBAR
# =========================================================

modo_visual = st.sidebar.radio("Modo visual", ["Claro", "Oscuro"], horizontal=True, index=0)
aplicar_estilo(modo_visual)

st.sidebar.title("Heras MatchLab")
st.sidebar.caption("Motor de planificación deportiva | Noname")

archivo = st.sidebar.file_uploader("Subir CSV de jugadores", type=["csv"])
if archivo is not None:
    tmp = pd.read_csv(archivo)
    norm, faltan = normalizar_df(tmp)
    if faltan:
        st.sidebar.error("Faltan columnas: " + ", ".join(faltan))
    else:
        st.session_state.players = norm
        st.sidebar.success("CSV cargado correctamente.")

if st.sidebar.button("Restaurar datos ejemplo"):
    st.session_state.players = datos_ejemplo()
    st.session_state.rivals = datos_rivales_ejemplo()
    st.sidebar.success("Datos restaurados.")

st.sidebar.markdown("---")
modelo = st.sidebar.selectbox("Modelo de juego", list(PRESETS_MODELO.keys()), index=0)

st.sidebar.subheader("Pesos del motor")
pesos = {}
for m in METRICAS:
    pesos[m] = st.sidebar.slider(NOMBRES_METRICAS[m], 0, 10, PRESETS_MODELO[modelo][m])

# =========================================================
# CÁLCULO
# =========================================================

df = st.session_state.players.copy()
df["score_modelo"] = df.apply(lambda r: score_jugador(r, pesos), axis=1)
df["nivel"] = df["score_modelo"].apply(nivel)
df["semaforo"] = df["score_modelo"].apply(semaforo)

propios = df[df["tipo"].str.lower() == "propio"].copy()
mercado = df[df["tipo"].str.lower().isin(["mercado", "recambio", "rival"])].copy()

# =========================================================
# CABECERA
# =========================================================

st.title("Heras MatchLab | Motor de planificación Noname")
st.caption("Modelo de juego · Scouting · Comparador · Presión según rival · XI ideal · Informes")

tabs = st.tabs([
    "📌 Resumen",
    "🧠 Modelo Noname",
    "🔎 Scouting",
    "🔁 Comparador",
    "🎯 Motor de presión",
    "🧩 XI ideal",
    "📝 Informes / Exportar"
])

# =========================================================
# RESUMEN
# =========================================================

with tabs[0]:
    st.header("Resumen ejecutivo")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Jugadores", len(df))
    c2.metric("Propios", len(propios))
    c3.metric("Mercado/Rivales", len(mercado))
    c4.metric("Score plantilla", round(propios["score_modelo"].mean(), 2) if not propios.empty else 0)
    c5.metric("Score mercado", round(mercado["score_modelo"].mean(), 2) if not mercado.empty else 0)

    col_a, col_b = st.columns([1.25, 1])

    with col_a:
        st.subheader("Ranking plantilla propia")
        st.dataframe(
            propios[["semaforo","nombre","posicion","rol","edad","minutos","score_modelo","nivel","estado","drivers"]]
            .sort_values("score_modelo", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    with col_b:
        st.subheader("Lectura del modelo")
        st.info(diagnostico_modelo(pesos))
        if not propios.empty:
            st.subheader("Encaje medio por posición")
            st.bar_chart(propios.groupby("posicion")["score_modelo"].mean().sort_values(ascending=False))

    st.subheader("Top mercado recomendado")
    st.dataframe(
        mercado[["semaforo","nombre","equipo","posicion","rol","edad","score_modelo","nivel","confianza","drivers"]]
        .sort_values("score_modelo", ascending=False).head(10),
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# MODELO NONAME
# =========================================================

with tabs[1]:
    st.header("Modelo de juego Noname")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"<div class='card'><b>Sistema nominal</b><br>{MODELO_NONAME['sistema_nominal']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><b>Interpretación real</b><br>{MODELO_NONAME['estructura_real']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><b>Sistema alternativo</b><br>{MODELO_NONAME['sistema_alternativo']}</div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='card'><b>Salida</b><br>{MODELO_NONAME['salida']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><b>Amplitud</b><br>{MODELO_NONAME['amplitud']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><b>Rest-defence</b><br>{MODELO_NONAME['rest_defence']}</div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='card'><b>Presión</b><br>{MODELO_NONAME['presion']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><b>Orientación</b><br>{MODELO_NONAME['orientacion']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'><b>Transición ofensiva</b><br>{MODELO_NONAME['transicion_ofensiva']}</div>", unsafe_allow_html=True)

    st.subheader("Pesos actuales del motor")
    pesos_df = pd.DataFrame({"Principio": [NOMBRES_METRICAS[m] for m in METRICAS], "Peso": [pesos[m] for m in METRICAS]}).set_index("Principio")
    st.bar_chart(pesos_df)

    st.subheader("Editor de jugadores")
    st.write("Puedes editar datos en sesión. Para guardarlo permanentemente, exporta el CSV y súbelo al repo.")
    edited = st.data_editor(st.session_state.players, use_container_width=True, num_rows="dynamic")
    if st.button("Guardar cambios de plantilla en sesión"):
        st.session_state.players = edited
        st.success("Cambios guardados en esta sesión.")

# =========================================================
# SCOUTING
# =========================================================

with tabs[2]:
    st.header("Scouting y búsqueda de perfiles")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        buscador = st.text_input("Buscar nombre")
        pos = st.multiselect("Posición", sorted(df["posicion"].unique()), default=sorted(df["posicion"].unique()))
    with f2:
        tipo = st.multiselect("Tipo", sorted(df["tipo"].unique()), default=sorted(df["tipo"].unique()))
        equipo = st.multiselect("Equipo", sorted(df["equipo"].unique()), default=sorted(df["equipo"].unique()))
    with f3:
        edad = st.slider("Edad", 16, 45, (18, 32))
        score_min = st.slider("Score mínimo", 0.0, 10.0, 6.0, 0.1)
    with f4:
        modo = st.radio("Modo de ranking", ["Score", "Similitud"], horizontal=True)
        solo_mercado = st.checkbox("Solo mercado", value=False)

    base = df[
        (df["posicion"].isin(pos)) &
        (df["tipo"].isin(tipo)) &
        (df["equipo"].isin(equipo)) &
        (df["edad"].between(edad[0], edad[1])) &
        (df["score_modelo"] >= score_min)
    ].copy()

    if buscador:
        base = base[base["nombre"].str.contains(buscador, case=False, na=False)]
    if solo_mercado:
        base = base[base["tipo"].str.lower().isin(["mercado","recambio","rival"])]

    if modo == "Similitud" and not df.empty:
        ref_name = st.selectbox("Jugador referencia", df["nombre"].tolist())
        ref = df[df["nombre"] == ref_name].iloc[0]
        misma_pos = st.checkbox("Solo misma posición que referencia", value=True)
        if misma_pos:
            base = base[base["posicion"] == ref["posicion"]].copy()
        base["similitud"] = base.apply(lambda r: similitud(r, ref, pesos), axis=1)
        base = base.sort_values(["similitud", "score_modelo"], ascending=False)
        columnas = ["semaforo","nombre","equipo","tipo","posicion","edad","score_modelo","similitud","nivel","drivers"]
    else:
        base = base.sort_values("score_modelo", ascending=False)
        columnas = ["semaforo","nombre","equipo","tipo","posicion","edad","score_modelo","nivel","confianza","drivers"]

    st.dataframe(base[columnas], use_container_width=True, hide_index=True)

    if not base.empty:
        st.subheader("Detalle del perfil")
        det_name = st.selectbox("Jugador para detalle", base["nombre"].tolist())
        det = base[base["nombre"] == det_name].iloc[0]
        d1, d2 = st.columns([1, 1.2])
        with d1:
            st.metric("Score", det["score_modelo"])
            st.metric("Nivel", det["nivel"])
            st.write(f"**Equipo:** {det['equipo']}")
            st.write(f"**Posición:** {det['posicion']}")
            st.write(f"**Rol:** {det['rol']}")
            st.write(f"**Drivers:** {det['drivers']}")
            st.write(f"**Observación:** {det['observacion']}")
        with d2:
            chart = pd.DataFrame({"Métrica": [NOMBRES_METRICAS[m] for m in METRICAS], "Valor": [det[m] for m in METRICAS]}).set_index("Métrica")
            st.bar_chart(chart)

# =========================================================
# COMPARADOR
# =========================================================

with tabs[3]:
    st.header("Comparador jugador propio vs recambios")

    propios_names = propios["nombre"].tolist() if not propios.empty else df["nombre"].tolist()
    jugador_a = st.selectbox("Jugador propio/base", propios_names)
    row_a = df[df["nombre"] == jugador_a].iloc[0]

    candidatos_b = df[df["posicion"].isin(MAPEO_PUESTOS.get(row_a["posicion"], [row_a["posicion"]]))]["nombre"].tolist()
    if len(candidatos_b) == 0:
        candidatos_b = df["nombre"].tolist()

    jugador_b = st.selectbox("Recambio/comparado", candidatos_b)
    row_b = df[df["nombre"] == jugador_b].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='card'><h3>{row_a['nombre']}</h3><b>{row_a['posicion']} · {row_a['rol']}</b><br>Score: {row_a['score_modelo']}<br>{row_a['drivers']}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='card'><h3>{row_b['nombre']}</h3><b>{row_b['posicion']} · {row_b['rol']}</b><br>Score: {row_b['score_modelo']}<br>{row_b['drivers']}</div>", unsafe_allow_html=True)

    comp = pd.DataFrame({
        "Métrica": [NOMBRES_METRICAS[m] for m in METRICAS],
        row_a["nombre"]: [row_a[m] for m in METRICAS],
        row_b["nombre"]: [row_b[m] for m in METRICAS],
        "Diferencia B-A": [round(row_b[m] - row_a[m], 2) for m in METRICAS]
    })

    cc1, cc2 = st.columns([1, 1])
    with cc1:
        st.dataframe(comp, use_container_width=True, hide_index=True)
    with cc2:
        st.bar_chart(comp.set_index("Métrica")[[row_a["nombre"], row_b["nombre"]]])

    if row_b["score_modelo"] > row_a["score_modelo"]:
        st.success(f"{row_b['nombre']} mejora el encaje global en el modelo actual ({row_b['score_modelo']} vs {row_a['score_modelo']}).")
    elif row_b["score_modelo"] < row_a["score_modelo"]:
        st.warning(f"{row_b['nombre']} no mejora el score global, aunque puede aportar matices concretos.")
    else:
        st.info("Ambos perfiles tienen un score similar. La decisión depende del rol y del contexto.")

# =========================================================
# MOTOR DE PRESIÓN
# =========================================================

with tabs[4]:
    st.header("Motor de presión según rival")

    r1, r2, r3 = st.columns(3)
    with r1:
        sistema_rival = st.selectbox("Sistema rival", ["4-4-2", "4-3-3", "4-2-3-1", "3-5-2", "3-4-2-1", "5-3-2"])
        salida_rival = st.selectbox("Estructura de salida rival", list(REGLAS_PRESION.keys()), index=1)
    with r2:
        bloque_rival = st.selectbox("Bloque rival", ["Bloque alto", "Bloque medio", "Bloque bajo"], index=1)
        amenaza = st.selectbox("Amenaza principal", ["Juego directo", "Juego interior", "Banda y centros", "Transición rápida", "Segunda jugada"])
    with r3:
        lateral_bajo = st.checkbox("El rival baja un lateral a salida", value=False)
        rival_dos_puntas = st.checkbox("El rival juega con dos puntas", value=False)

    if lateral_bajo:
        salida_ajustada = "Lateral bajo en salida"
    elif sistema_rival.startswith("3"):
        salida_ajustada = "Salida de 3"
    else:
        salida_ajustada = salida_rival

    plan = generar_plan_presion(salida_ajustada, sistema_rival, bloque_rival)
    st.markdown(plan)

    st.subheader("Lectura complementaria")
    if rival_dos_puntas:
        st.info("Si el rival juega con dos puntas, gana sentido activar el 3-4-3 para tener superioridad numérica en salida y formar cuadrado interior.")
    if amenaza == "Banda y centros":
        st.warning("Prioridad defensiva: defender área, cerrar zona de remate y proteger segundo palo/rechace.")
    elif amenaza == "Juego interior":
        st.warning("Prioridad defensiva: cerrar dentro, impedir recepción de pivotes/mediapuntas y forzar fuera.")
    elif amenaza == "Transición rápida":
        st.warning("Prioridad defensiva: rest-defence estable, lateral corto preparado y pivote en contención.")

    st.subheader("Base de rivales editable")
    st.session_state.rivals = st.data_editor(st.session_state.rivals, use_container_width=True, num_rows="dynamic")

# =========================================================
# XI IDEAL
# =========================================================

with tabs[5]:
    st.header("XI ideal y estructura sobre campo")

    x1, x2, x3 = st.columns(3)
    with x1:
        formacion = st.selectbox("Estructura", list(FORMACIONES.keys()), index=0)
    with x2:
        fuente = st.radio("Fuente", ["Solo propios", "Solo mercado", "Mixto"], horizontal=True)
    with x3:
        score_corte = st.slider("Score mínimo para XI", 0.0, 10.0, 0.0, 0.1)

    if fuente == "Solo propios":
        pool = propios.copy()
    elif fuente == "Solo mercado":
        pool = mercado.copy()
    else:
        pool = df.copy()

    pool = pool[pool["score_modelo"] >= score_corte].copy()
    xi, banquillo = construir_xi(pool, formacion)

    st.markdown(render_pizarra(xi, modo_visual), unsafe_allow_html=True)

    xi_df = pd.DataFrame(xi)[["slot","nombre","equipo","posicion","rol","score_modelo","vacante"]]
    st.subheader("XI seleccionado")
    st.dataframe(xi_df, use_container_width=True, hide_index=True)

    vacantes = xi_df[xi_df["vacante"] == True]
    if not vacantes.empty:
        st.error("Vacantes detectadas: " + ", ".join(vacantes["slot"].tolist()))
    else:
        st.success("XI completo según fuente y modelo seleccionados.")

    st.subheader("Banquillo recomendado")
    if not banquillo.empty:
        st.dataframe(
            banquillo[["nombre","equipo","posicion","rol","score_modelo","nivel","estado"]],
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Reglas tácticas de la estructura")
    if formacion == "4-2-3-1 Noname":
        st.write("- Base 4-2-3-1 que se interpreta como 4-4-2 por rol libre del mediapunta.")
        st.write("- Laterales asimétricos: uno largo y otro corto/interior para preparar pérdida.")
        st.write("- Extremos en amplitud; si uno va dentro, el lado contrario debe conservar amplitud.")
    elif formacion == "4-4-2 real: MP segundo punta":
        st.write("- Delantero + mediapunta forman la primera línea de presión.")
        st.write("- El mediapunta puede venir de cara, conectar juego y atacar intervalo después.")
    else:
        st.write("- 3-4-3 con carriles altos y cuadrado interior de dos pivotes + dos mediapuntas.")
        st.write("- Útil ante dos puntas rivales o rivales con tres dentro para igualar/superar mediocampo.")

# =========================================================
# INFORMES / EXPORTAR
# =========================================================

with tabs[6]:
    st.header("Informes y exportación")

    sub1, sub2, sub3 = st.tabs(["Jugador", "Modelo", "CSV"])

    with sub1:
        j = st.selectbox("Jugador para informe", df["nombre"].tolist())
        row = df[df["nombre"] == j].iloc[0]
        texto = informe_jugador(row)
        st.text_area("Informe individual", texto, height=360)
        st.download_button("Descargar informe jugador", texto, file_name=f"informe_{row['nombre'].replace(' ', '_')}.txt", mime="text/plain")

    with sub2:
        texto_modelo = informe_modelo() + "\n\n" + diagnostico_modelo(pesos)
        st.text_area("Informe del modelo Noname", texto_modelo, height=420)
        st.download_button("Descargar informe modelo", texto_modelo, file_name="modelo_juego_noname.txt", mime="text/plain")

    with sub3:
        ranking = df.sort_values("score_modelo", ascending=False)
        st.download_button(
            "Exportar ranking CSV",
            ranking.to_csv(index=False).encode("utf-8"),
            file_name=f"ranking_heras_matchlab_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.download_button(
            "Exportar plantilla base CSV",
            st.session_state.players.to_csv(index=False).encode("utf-8"),
            file_name="plantilla_base_noname.csv",
            mime="text/csv"
        )
        st.download_button(
            "Exportar rivales CSV",
            st.session_state.rivals.to_csv(index=False).encode("utf-8"),
            file_name="rivales_noname.csv",
            mime="text/csv"
        )

        st.subheader("Columnas necesarias para CSV de jugadores")
        st.code(", ".join(["nombre","equipo","tipo","liga","posicion","rol","edad","minutos"] + METRICAS + ["confianza","estado","drivers","observacion"]))