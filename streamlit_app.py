from pathlib import Path
import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Heras MatchLab | Noname V8", page_icon="⚽", layout="wide")

JUGADORES_CSV = "jugadores_noname.csv"
OJEADOS_CSV = "jugadores_ojeados_noname.csv"

ENCAJES = [
    "encaje_modelo_general", "encaje_4231_442", "encaje_343", "encaje_presion_alta",
    "encaje_bloque_medio", "encaje_salida_balon", "encaje_juego_directo_segunda_jugada",
    "encaje_transicion_ofensiva", "encaje_transicion_defensiva", "encaje_rest_defence", "encaje_abp"
]

NOMBRES = {
    "encaje_modelo_general": "Modelo general",
    "encaje_4231_442": "4-2-3-1 / 4-4-2",
    "encaje_343": "3-4-3",
    "encaje_presion_alta": "Presión alta",
    "encaje_bloque_medio": "Bloque medio",
    "encaje_salida_balon": "Salida balón",
    "encaje_juego_directo_segunda_jugada": "Juego directo / 2ª jugada",
    "encaje_transicion_ofensiva": "Transición ofensiva",
    "encaje_transicion_defensiva": "Transición defensiva",
    "encaje_rest_defence": "Rest-defence",
    "encaje_abp": "ABP",
}

COLORS = {
    "Renovar": "#16A34A",
    "Renovar con rol secundario": "#2563EB",
    "Duda": "#D97706",
    "Pendiente de evaluación": "#7C3AED",
    "No ofrecer renovación": "#DC2626",
    "Objetivo mercado": "#0EA5E9",
    "Seguimiento": "#64748B",
    "Descartar": "#111827",
    "Vacante": "#334155",
}

POSICIONES = ["POR", "LD", "LI", "DFC", "MCD", "MC", "MCO", "ED", "EI", "DC"]

DECISIONES_PROPIAS = ["Renovar", "Renovar con rol secundario", "Duda", "Pendiente de evaluación", "No ofrecer renovación"]
DECISIONES_OJEO = ["Objetivo mercado", "Seguimiento", "Pendiente de evaluación", "Descartar"]

BLOQUES = {
    "Portería": ["POR"],
    "Lateral derecho": ["LD"],
    "Lateral izquierdo": ["LI"],
    "Centrales": ["DFC"],
    "Mediocentros": ["MCD", "MC"],
    "Mediapunta": ["MCO"],
    "Extremos": ["ED", "EI"],
    "Delanteros": ["DC"],
}

NECESIDADES = [
    {"necesidad": "Portero titular", "posiciones": ["POR"], "min_ok": 1, "motivo": "Se necesita un portero titular fiable y estable."},
    {"necesidad": "Lateral derecho", "posiciones": ["LD"], "min_ok": 1, "motivo": "La continuidad del carril derecho está abierta."},
    {"necesidad": "Recambio lateral izquierdo", "posiciones": ["LI", "EI"], "min_ok": 2, "motivo": "Raúl Crespo necesita un recambio real."},
    {"necesidad": "Central de rotación", "posiciones": ["DFC", "LD"], "min_ok": 4, "motivo": "Hace falta profundidad y corrección en la línea defensiva."},
    {"necesidad": "Mediocentro con pie", "posiciones": ["MC", "MCD"], "min_ok": 4, "motivo": "El equipo necesita pausa, pase y continuidad en el doble pivote."},
    {"necesidad": "6 competitivo", "posiciones": ["MCD", "MC"], "min_ok": 2, "motivo": "Mati necesita competencia/complemento de nivel."},
    {"necesidad": "Extremo intenso", "posiciones": ["ED", "EI"], "min_ok": 4, "motivo": "Se necesita banda con presión, amplitud y continuidad."},
    {"necesidad": "Delantero referencia", "posiciones": ["DC"], "min_ok": 2, "motivo": "La posición de 9 es prioridad: fijación, descarga, área y presión."},
]

MODELO = [
    ("Sistema base", "4-2-3-1 interpretado como 4-4-2 con mediapunta / segundo punta libre."),
    ("Alternativa", "3-4-3 con carriles altos y cuadrado interior."),
    ("Salida", "Salida de 4, laterales asimétricos: uno largo y otro corto/interior."),
    ("Presión", "Bloque alto. Delantero + mediapunta inician. Cerrar dentro y forzar fuera."),
    ("Transición ofensiva", "Vertical tras robo, buscando mediapunta libre, delantero o espacio."),
    ("Transición defensiva", "Presión tras pérdida; si se supera, embudo interior y reorganización."),
    ("Rest-defence", "3+2 o 3+1 según altura de pivotes y laterales."),
    ("ABP", "Importante por perfiles de centrales, 9 y jugadores de rechace/frontal."),
]

PESOS_BASE = {
    "encaje_modelo_general": 2.0, "encaje_4231_442": 1.2, "encaje_343": 0.6,
    "encaje_presion_alta": 1.2, "encaje_bloque_medio": 0.7, "encaje_salida_balon": 0.9,
    "encaje_juego_directo_segunda_jugada": 0.8, "encaje_transicion_ofensiva": 0.9,
    "encaje_transicion_defensiva": 1.1, "encaje_rest_defence": 1.0, "encaje_abp": 0.6,
}

PRESETS = {
    "Modelo equilibrado": PESOS_BASE,
    "Presión alta + rest-defence": {**PESOS_BASE, "encaje_presion_alta": 2.4, "encaje_rest_defence": 2.1, "encaje_transicion_defensiva": 1.8},
    "Salida + pausa": {**PESOS_BASE, "encaje_salida_balon": 2.3, "encaje_4231_442": 1.7, "encaje_bloque_medio": 1.2},
    "Juego directo + área": {**PESOS_BASE, "encaje_juego_directo_segunda_jugada": 2.1, "encaje_abp": 1.9, "encaje_transicion_ofensiva": 1.4},
    "Plan 3-4-3": {**PESOS_BASE, "encaje_343": 2.4, "encaje_presion_alta": 1.4, "encaje_transicion_ofensiva": 1.3},
}

SLOTS_4231 = [
    ("POR", 50, 90), ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
    ("MCD", 40, 58), ("MC", 60, 58), ("EI", 18, 39), ("MCO", 50, 39), ("ED", 82, 39), ("DC", 50, 18)
]
SLOTS_343 = [
    ("POR", 50, 90), ("DFC", 28, 76), ("DFC", 50, 78), ("DFC", 72, 76),
    ("LI", 15, 55), ("MCD", 40, 56), ("MC", 60, 56), ("LD", 85, 55),
    ("MCO", 40, 34), ("MCO", 60, 34), ("DC", 50, 18)
]
MAPEO = {
    "POR": ["POR"], "LD": ["LD", "DFC"], "LI": ["LI", "EI"], "DFC": ["DFC", "LD", "LI"],
    "MCD": ["MCD", "MC"], "MC": ["MC", "MCD", "MCO"], "MCO": ["MCO", "DC", "ED", "EI", "MC"],
    "ED": ["ED", "EI", "MCO", "DC"], "EI": ["EI", "ED", "MCO", "DC"], "DC": ["DC", "MCO", "EI", "ED"]
}

st.markdown("""
<style>
.stApp{background:linear-gradient(180deg,#F8FAFC 0%,#EEF2F7 100%);color:#0F172A;}
section[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E2E8F0;}
h1,h2,h3,h4{color:#0F172A!important;}
div[data-testid="stMetric"]{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:18px;padding:16px;box-shadow:0 8px 24px rgba(15,23,42,.06);}
.hero{background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 55%,#0EA5E9 100%);color:white;border-radius:24px;padding:26px 30px;margin-bottom:18px;box-shadow:0 16px 40px rgba(15,23,42,.20);}
.hero h1{color:white!important;margin:0;font-size:34px;}
.hero p{color:#DBEAFE;margin:8px 0 0 0;font-size:15px;}
.card{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:18px;padding:16px;margin-bottom:12px;box-shadow:0 8px 24px rgba(15,23,42,.06);}
.card-tight{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;padding:12px;margin-bottom:10px;box-shadow:0 4px 14px rgba(15,23,42,.05);}
.small{font-size:12px;color:#64748B;}
.pill{display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;margin:2px 4px 2px 0;color:white;}
.need{border-left:5px solid #2563EB;padding:12px 14px;background:#FFFFFF;border-radius:14px;margin-bottom:10px;box-shadow:0 4px 14px rgba(15,23,42,.05);}
.need-title{font-weight:800;font-size:15px;}
.need-text{color:#475569;font-size:13px;margin-top:3px;}
hr{border:none;border-top:1px solid #E2E8F0;margin:12px 0;}
</style>
""", unsafe_allow_html=True)

def esc(x):
    return html.escape("" if pd.isna(x) else str(x))

def read_csv(uploaded, default_path):
    if uploaded is not None:
        return pd.read_csv(uploaded, encoding="utf-8-sig")
    if Path(default_path).exists():
        return pd.read_csv(default_path, encoding="utf-8-sig")
    return pd.DataFrame()

def clean_df(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in ENCAJES:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    for col in df.columns:
        if col not in ENCAJES:
            df[col] = df[col].fillna("").astype(str)
    if "decision_deportiva" not in df.columns:
        df["decision_deportiva"] = "Pendiente de evaluación"
    df["decision_deportiva"] = df["decision_deportiva"].replace("", "Pendiente de evaluación")
    if "tipo" not in df.columns:
        df["tipo"] = ""
    if "posicion_secundaria" not in df.columns:
        df["posicion_secundaria"] = ""
    return df

def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def color_decision(decision):
    return COLORS.get(str(decision), "#64748B")

def decision_label(decision):
    return {
        "Renovar": "🟢 Renovar", "Renovar con rol secundario": "🔵 Rol secundario", "Duda": "🟡 Duda",
        "Pendiente de evaluación": "🟣 Pendiente", "No ofrecer renovación": "🔴 No renovar",
        "Objetivo mercado": "⭐ Objetivo", "Seguimiento": "👁️ Seguimiento", "Descartar": "⚫ Descartar",
        "Vacante": "⚪ Vacante",
    }.get(decision, decision)

def norm_pos(pos):
    pos = str(pos or "").upper().strip()
    return [p.strip() for p in pos.replace("-", "/").split("/") if p.strip()] if pos else []

def has_pos(row, allowed):
    positions = norm_pos(row.get("posicion_principal", "")) + norm_pos(row.get("posicion_secundaria", ""))
    return any(p in allowed for p in positions)

def by_pos(df, allowed):
    if df.empty:
        return df
    return df[df.apply(lambda r: has_pos(r, allowed), axis=1)].copy()

def weighted_score(df, weights):
    total = sum(float(v) for v in weights.values()) or 1
    score = pd.Series(0.0, index=df.index)
    for col, w in weights.items():
        if col in df.columns:
            score += df[col].astype(float) * float(w)
    return (score / total).round(2)

def apply_scores(df, weights):
    df = df.copy()
    df["score_modelo"] = weighted_score(df, weights)
    return df

def player_card(row, compact=False):
    decision = row.get("decision_deportiva", "")
    color = color_decision(decision)
    score = float(row.get("score_modelo", row.get("encaje_modelo_general", 0)))
    extra = "" if compact else f'<div class="small" style="margin-top:8px;">{esc(row.get("conclusion",""))}</div>'
    return (
        f'<div class="card-tight" style="border-left:5px solid {color};">'
        f'<div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start;">'
        f'<div><div style="font-weight:900;font-size:16px;">{esc(row.get("nombre",""))}</div>'
        f'<div class="small">{esc(row.get("equipo",""))} · {esc(row.get("posicion_principal",""))} · {esc(row.get("rol_ideal","") or row.get("rol_actual",""))}</div></div>'
        f'<div style="text-align:right;"><div style="font-size:24px;font-weight:900;color:{color};">{score:.1f}</div><div class="small">score</div></div>'
        f'</div><div style="margin-top:8px;"><span class="pill" style="background:{color};">{esc(decision_label(decision))}</span></div>{extra}</div>'
    )

def pick_xi(df, slots, fuente):
    data = df.copy()
    if fuente == "Solo propios":
        data = data[data["tipo"].str.lower().eq("propio")]
    elif fuente == "Solo ojeados":
        data = data[data["tipo"].str.lower().isin(["ojeado", "mercado", "rival", "recambio"])]
    elif fuente == "Propios renovables":
        data = data[data["decision_deportiva"].isin(["Renovar", "Renovar con rol secundario", "Duda", "Pendiente de evaluación"])]

    used, output = set(), []
    for slot, x, y in slots:
        candidates = by_pos(data[~data["nombre"].isin(used)], MAPEO.get(slot, [slot]))
        if candidates.empty:
            output.append({"slot": slot, "x": x, "y": y, "nombre": "VACANTE", "score": 0, "decision": "Vacante", "rol": "Necesidad de mercado", "equipo": ""})
            continue
        def slot_score(r):
            base = float(r.get("score_modelo", r.get("encaje_modelo_general", 0)))
            positions = norm_pos(r.get("posicion_principal", "")) + norm_pos(r.get("posicion_secundaria", ""))
            return base + (0.35 if slot in positions else 0)
        candidates["_slot_score"] = candidates.apply(slot_score, axis=1)
        pick = candidates.sort_values(["_slot_score", "score_modelo"], ascending=False).iloc[0]
        used.add(pick["nombre"])
        output.append({
            "slot": slot, "x": x, "y": y, "nombre": pick.get("nombre",""), "score": float(pick.get("score_modelo", 0)),
            "decision": pick.get("decision_deportiva",""), "rol": pick.get("rol_proxima_temporada","") or pick.get("rol_ideal",""), "equipo": pick.get("equipo","")
        })
    return output

def render_pitch(players):
    css = """
<style>
body{margin:0;background:transparent;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;}
.pitch{position:relative;height:660px;border-radius:24px;overflow:hidden;border:4px solid #D9F99D;background:repeating-linear-gradient(90deg,#15803D 0 10%,#16A34A 10% 20%);box-shadow:inset 0 0 0 2px rgba(255,255,255,.45),0 18px 40px rgba(15,23,42,.16);}
.pitch:before{content:"";position:absolute;left:50%;top:0;bottom:0;width:2px;background:rgba(255,255,255,.65);}
.circle{position:absolute;left:calc(50% - 62px);top:calc(50% - 62px);width:124px;height:124px;border:2px solid rgba(255,255,255,.65);border-radius:50%;}
.box-top,.box-bottom{position:absolute;left:23%;width:54%;height:18%;border:2px solid rgba(255,255,255,.65);}
.box-top{top:8%;}.box-bottom{bottom:8%;}
.player-dot{position:absolute;width:142px;min-height:72px;transform:translate(-71px,-36px);background:rgba(255,255,255,.96);border:2px solid #0F172A;border-radius:16px;text-align:center;padding:10px 7px;box-shadow:0 8px 22px rgba(15,23,42,.22);color:#0F172A;}
.player-score{position:absolute;top:-17px;left:50%;transform:translateX(-50%);width:36px;height:36px;line-height:32px;border-radius:999px;color:white;font-weight:900;font-size:12px;border:2px solid white;}
.player-name{margin-top:7px;font-weight:900;font-size:13px;line-height:1.1;}
.player-role{color:#64748B;font-size:10px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.slot{color:#B45309;font-weight:800;font-size:10px;}
</style>
"""
    parts = [css, '<div class="pitch"><div class="circle"></div><div class="box-top"></div><div class="box-bottom"></div>']
    for p in players:
        color = color_decision(p["decision"])
        score = "--" if p["score"] <= 0 else f"{p['score']:.1f}"
        parts.append(
            f'<div class="player-dot" style="left:{p["x"]}%;top:{p["y"]}%;border-color:{color};">'
            f'<div class="player-score" style="background:{color};">{score}</div>'
            f'<div class="player-name">{esc(p["nombre"])}</div>'
            f'<div class="slot">{esc(p["slot"])} · {esc(p["equipo"])}</div>'
            f'<div class="player-role">{esc(p["rol"])}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)

def market_needs(jugadores, ojeados):
    needs = []
    for n in NECESIDADES:
        propios = by_pos(jugadores, n["posiciones"])
        ok = propios[propios["decision_deportiva"].isin(["Renovar", "Renovar con rol secundario"])]
        riesgo = propios[propios["decision_deportiva"].isin(["Duda", "Pendiente de evaluación", "No ofrecer renovación"])]
        candidatos = by_pos(ojeados, n["posiciones"])
        candidatos = candidatos[candidatos["decision_deportiva"].isin(["Objetivo mercado", "Seguimiento", "Pendiente de evaluación", ""])]
        candidatos = candidatos.sort_values("score_modelo", ascending=False)
        if len(ok) == 0:
            prioridad = "Crítica"
        elif len(ok) < n["min_ok"] or len(riesgo) >= 1:
            prioridad = "Alta"
        elif len(candidatos) == 0:
            prioridad = "Media"
        else:
            prioridad = "Controlada"
        needs.append({**n, "prioridad": prioridad, "candidatos": candidatos, "propios": propios, "ok": ok, "riesgo": riesgo})
    return needs

def columns_config(kind):
    decisions = DECISIONES_OJEO if kind == "ojeo" else DECISIONES_PROPIAS
    config = {
        "id_jugador": st.column_config.TextColumn("ID"),
        "nombre": st.column_config.TextColumn("Nombre"),
        "equipo": st.column_config.TextColumn("Equipo"),
        "tipo": st.column_config.SelectboxColumn("Tipo", options=["Propio", "Ojeado", "Mercado", "Rival", "Recambio"]),
        "posicion_principal": st.column_config.SelectboxColumn("Posición", options=POSICIONES),
        "decision_deportiva": st.column_config.SelectboxColumn("Decisión", options=decisions),
        "prioridad_renovacion": st.column_config.SelectboxColumn("Prioridad", options=["Alta","Media","Baja","No renovar","Pendiente",""]),
        "riesgo_continuidad": st.column_config.SelectboxColumn("Riesgo", options=["Bajo","Medio","Alto","Pendiente",""]),
        "encaje_modelo_general": st.column_config.NumberColumn("Modelo", min_value=0, max_value=10, step=0.1, format="%.1f"),
    }
    for col in ENCAJES:
        config[col] = st.column_config.NumberColumn(NOMBRES.get(col, col), min_value=0, max_value=10, step=0.1, format="%.1f")
    return config

def ficha(df, nombre):
    row = df[df["nombre"] == nombre].iloc[0]
    color = color_decision(row.get("decision_deportiva", ""))
    st.markdown(
        f'<div class="card" style="border-left:6px solid {color};">'
        f'<div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;">'
        f'<div><div class="small">{esc(row.get("tipo",""))} · {esc(row.get("equipo",""))}</div>'
        f'<h2 style="margin:0;">{esc(row.get("nombre",""))}</h2><div class="small">{esc(row.get("nombre_oficial",""))}</div></div>'
        f'<div style="text-align:right;"><div style="font-size:36px;font-weight:900;color:{color};">{float(row.get("score_modelo",0)):.1f}</div>'
        f'<div class="small">score ponderado</div></div></div>'
        f'<div style="margin-top:12px;"><span class="pill" style="background:{color};">{esc(decision_label(row.get("decision_deportiva","")))}</span>'
        f'<span class="pill" style="background:#0F172A;">{esc(row.get("posicion_principal",""))}</span>'
        f'<span class="pill" style="background:#64748B;">Riesgo: {esc(row.get("riesgo_continuidad",""))}</span></div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.info(f"**Rol actual**\n\n{row.get('rol_actual','') or '—'}")
    c2.info(f"**Rol ideal**\n\n{row.get('rol_ideal','') or '—'}")
    c3.info(f"**Rol próxima temporada**\n\n{row.get('rol_proxima_temporada','') or '—'}")
    col1, col2 = st.columns([1.15, 1])
    with col1:
        enc = pd.DataFrame({"Encaje": [NOMBRES.get(c, c) for c in ENCAJES], "Valor": [float(row.get(c, 0)) for c in ENCAJES]}).set_index("Encaje")
        st.subheader("Mapa de encaje")
        st.bar_chart(enc)
    with col2:
        st.subheader("Lectura rápida")
        st.write("**Fortalezas**")
        st.write(row.get("fortalezas", ""))
        st.write("**Debilidades**")
        st.write(row.get("debilidades", ""))
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Dónde rinde**\n\n{row.get('contexto_donde_rinde','')}")
    with c2:
        st.warning(f"**Dónde sufre**\n\n{row.get('contexto_donde_sufre','')}")
    st.subheader("Observación táctica")
    st.info(row.get("observacion_tactica", ""))
    st.subheader("Conclusión")
    st.write(row.get("conclusion", ""))

# CARGA
st.sidebar.title("Heras MatchLab V8")
st.sidebar.caption("Planificación interactiva + ojeo")
st.sidebar.markdown("---")
uploaded_jug = st.sidebar.file_uploader("Subir jugadores_noname.csv", type=["csv"])
uploaded_ojeados = st.sidebar.file_uploader("Subir jugadores_ojeados_noname.csv", type=["csv"])

raw_jug = clean_df(read_csv(uploaded_jug, JUGADORES_CSV))
raw_oj = clean_df(read_csv(uploaded_ojeados, OJEADOS_CSV))
if raw_jug.empty:
    st.error("No se encontró jugadores_noname.csv.")
    st.stop()
if raw_oj.empty:
    raw_oj = pd.DataFrame(columns=raw_jug.columns)

if "jugadores_edit" not in st.session_state or uploaded_jug is not None:
    st.session_state.jugadores_edit = raw_jug.copy()
if "ojeados_edit" not in st.session_state or uploaded_ojeados is not None:
    st.session_state.ojeados_edit = raw_oj.copy()
if "shortlist" not in st.session_state:
    st.session_state.shortlist = pd.DataFrame(columns=["nombre", "equipo", "posicion_principal", "score_modelo", "decision_deportiva", "necesidad", "nota_shortlist"])
if "weights" not in st.session_state:
    st.session_state.weights = PESOS_BASE.copy()

st.sidebar.subheader("Modelo de ponderación")
preset = st.sidebar.selectbox("Preset", list(PRESETS.keys()))
if st.sidebar.button("Aplicar preset"):
    st.session_state.weights = PRESETS[preset].copy()
    st.rerun()
with st.sidebar.expander("Ajustar pesos", expanded=False):
    for col in ENCAJES:
        st.session_state.weights[col] = st.slider(NOMBRES.get(col, col), 0.0, 3.0, float(st.session_state.weights.get(col, PESOS_BASE[col])), 0.1, key=f"peso_{col}")

jugadores = clean_df(st.session_state.jugadores_edit)
ojeados = clean_df(st.session_state.ojeados_edit)
for col in jugadores.columns:
    if col not in ojeados.columns:
        ojeados[col] = ""
for col in ojeados.columns:
    if col not in jugadores.columns:
        jugadores[col] = ""
ojeados = ojeados[jugadores.columns]

jugadores = apply_scores(jugadores, st.session_state.weights)
ojeados = apply_scores(ojeados, st.session_state.weights)
todos = apply_scores(pd.concat([jugadores, ojeados], ignore_index=True), st.session_state.weights)

st.markdown('<div class="hero"><h1>Heras MatchLab · Noname V8</h1><p>Planificación interactiva, campograma configurable, mercado vivo, editor interno y score ponderado por modelo.</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["🏠 Dashboard", "🧩 Campograma", "✏️ Editor", "👁️ Mercado vivo", "🔁 Comparador", "👤 Ficha", "🧠 Modelo", "📤 Exportar"])

with tabs[0]:
    st.header("Dashboard de planificación")
    continuidad = int(jugadores["decision_deportiva"].isin(["Renovar", "Renovar con rol secundario"]).sum())
    dudas = int(jugadores["decision_deportiva"].isin(["Duda", "Pendiente de evaluación"]).sum())
    bajas = int((jugadores["decision_deportiva"] == "No ofrecer renovación").sum())
    objetivos = int(ojeados["decision_deportiva"].isin(["Objetivo mercado", "Seguimiento"]).sum()) if not ojeados.empty else 0
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Plantilla", len(jugadores)); c2.metric("Ojeados", len(ojeados)); c3.metric("Continuidad", continuidad); c4.metric("Dudas", dudas); c5.metric("Objetivos", objetivos)

    st.subheader("Diagnóstico por bloques")
    block_cols = st.columns(4)
    for idx, (bloque, posiciones) in enumerate(BLOQUES.items()):
        subset = by_pos(jugadores, posiciones)
        ok = subset[subset["decision_deportiva"].isin(["Renovar", "Renovar con rol secundario"])]
        riesgo = subset[subset["decision_deportiva"].isin(["Duda", "Pendiente de evaluación", "No ofrecer renovación"])]
        best = by_pos(ojeados, posiciones).sort_values("score_modelo", ascending=False).head(1)
        best_txt = "Sin ojeado" if best.empty else f"{best.iloc[0]['nombre']} · {float(best.iloc[0]['score_modelo']):.1f}"
        with block_cols[idx % 4]:
            st.markdown(f'<div class="card-tight"><div class="small">{esc(bloque)}</div><div style="font-size:26px;font-weight:900;">{len(ok)}/{len(subset)}</div><div class="small">continuidad clara / total</div><div style="margin-top:8px;"><span class="pill" style="background:#16A34A;">OK {len(ok)}</span><span class="pill" style="background:#DC2626;">Riesgo {len(riesgo)}</span></div><hr><div class="small"><b>Mejor ojeado:</b> {esc(best_txt)}</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.15, 1])
    with col1:
        st.subheader("Necesidades priorizadas")
        for need in market_needs(jugadores, ojeados):
            top = "Sin candidato cargado"
            if not need["candidatos"].empty:
                r = need["candidatos"].iloc[0]
                top = f"{r['nombre']} · {r['equipo']} · {float(r['score_modelo']):.1f}"
            color = {"Crítica": "#7F1D1D", "Alta": "#DC2626", "Media": "#D97706", "Controlada": "#16A34A"}.get(need["prioridad"], "#2563EB")
            st.markdown(f'<div class="need" style="border-left-color:{color};"><div class="need-title">{esc(need["necesidad"])} · {esc(need["prioridad"])}</div><div class="need-text">{esc(need["motivo"])}</div><div class="small" style="margin-top:6px;"><b>Mejor ojeado:</b> {esc(top)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.subheader("Top score ponderado")
        for _, r in jugadores.sort_values("score_modelo", ascending=False).head(7).iterrows():
            st.markdown(player_card(r, compact=True), unsafe_allow_html=True)

with tabs[1]:
    st.header("Campograma configurable")
    c1, c2, c3 = st.columns(3)
    estructura = c1.selectbox("Estructura", ["4-2-3-1 / 4-4-2", "3-4-3"])
    modo_xi = c2.selectbox("Modo de selección", ["Automático", "Manual"])
    fuente_xi = c3.selectbox("Fuente", ["Propios renovables", "Solo propios", "Solo ojeados", "Todos"])
    slots = SLOTS_4231 if estructura == "4-2-3-1 / 4-4-2" else SLOTS_343

    if modo_xi == "Automático":
        xi = pick_xi(todos, slots, fuente_xi)
    else:
        options = ["VACANTE"] + todos["nombre"].tolist()
        used, xi = [], []
        cols_manual = st.columns(4)
        for idx, (slot, x, y) in enumerate(slots):
            with cols_manual[idx % 4]:
                candidates = by_pos(todos, MAPEO.get(slot, [slot])).sort_values("score_modelo", ascending=False)
                default = candidates.iloc[0]["nombre"] if not candidates.empty else "VACANTE"
                selected = st.selectbox(f"{slot} {idx+1}", options, index=options.index(default) if default in options else 0, key=f"manual_{estructura}_{idx}_{slot}")
            if selected == "VACANTE" or selected in used:
                xi.append({"slot": slot, "x": x, "y": y, "nombre": "VACANTE", "score": 0, "decision": "Vacante", "rol": "Sin asignar", "equipo": ""})
            else:
                used.append(selected)
                row = todos[todos["nombre"] == selected].iloc[0]
                xi.append({"slot": slot, "x": x, "y": y, "nombre": row["nombre"], "score": float(row["score_modelo"]), "decision": row["decision_deportiva"], "rol": row.get("rol_proxima_temporada", "") or row.get("rol_ideal", ""), "equipo": row.get("equipo", "")})

    col1, col2 = st.columns([1.35, 1])
    with col1:
        components.html(render_pitch(xi), height=700, scrolling=False)
    with col2:
        xi_df = pd.DataFrame(xi)
        st.subheader("Lectura del XI")
        st.dataframe(xi_df[["slot", "nombre", "equipo", "score", "decision", "rol"]], use_container_width=True, hide_index=True)
        st.metric("Score medio XI", f"{xi_df[xi_df['score'] > 0]['score'].mean() if len(xi_df[xi_df['score']>0]) else 0:.2f}")
        st.metric("Vacantes", int((xi_df["nombre"] == "VACANTE").sum()))
        st.subheader("Ranking por posición")
        pos_select = st.selectbox("Ver posición", POSICIONES, index=POSICIONES.index("DC"))
        pos_df = by_pos(todos, [pos_select]).sort_values("score_modelo", ascending=False)
        st.dataframe(pos_df[["nombre", "equipo", "tipo", "decision_deportiva", "score_modelo", "rol_proxima_temporada"]], use_container_width=True, hide_index=True)

with tabs[2]:
    st.header("Editor de datos")
    st.info("Los cambios se guardan en esta sesión. Para conservarlos, descarga los CSV editados en Exportar.")
    editor_tab1, editor_tab2 = st.tabs(["Plantilla propia", "Lista de ojeo"])
    cols_front = ["id_jugador", "nombre", "nombre_oficial", "equipo", "tipo", "posicion_principal", "posicion_secundaria", "rol_actual", "rol_ideal", "decision_deportiva", "prioridad_renovacion", "riesgo_continuidad", "rol_proxima_temporada", "encaje_modelo_general", "conclusion"]
    with editor_tab1:
        visible = [c for c in cols_front if c in jugadores.columns]
        edited = st.data_editor(jugadores[visible], num_rows="dynamic", use_container_width=True, column_config=columns_config("propios"), key="editor_propios")
        if st.button("Aplicar cambios a plantilla", type="primary"):
            updated = jugadores.copy()
            for col in edited.columns:
                updated[col] = edited[col]
            st.session_state.jugadores_edit = updated.drop(columns=["score_modelo"], errors="ignore")
            st.success("Cambios aplicados.")
            st.rerun()
    with editor_tab2:
        visible = [c for c in cols_front if c in ojeados.columns]
        edited_o = st.data_editor(ojeados[visible], num_rows="dynamic", use_container_width=True, column_config=columns_config("ojeo"), key="editor_ojeo")
        if st.button("Aplicar cambios a ojeo", type="primary"):
            updated = ojeados.copy()
            for col in edited_o.columns:
                updated[col] = edited_o[col]
            st.session_state.ojeados_edit = updated.drop(columns=["score_modelo"], errors="ignore")
            st.success("Cambios aplicados.")
            st.rerun()

with tabs[3]:
    st.header("Mercado vivo")
    needs = market_needs(jugadores, ojeados)
    selected_need = st.selectbox("Necesidad", [n["necesidad"] for n in needs])
    need = next(n for n in needs if n["necesidad"] == selected_need)
    st.markdown(f'<div class="card"><div class="small">Prioridad: {esc(need["prioridad"])} · Posiciones: {", ".join(need["posiciones"])}</div><h3 style="margin:4px 0 8px 0;">{esc(need["necesidad"])}</h3><div>{esc(need["motivo"])}</div></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Situación interna")
        propios = need["propios"].sort_values("score_modelo", ascending=False)
        if propios.empty:
            st.warning("No hay jugadores propios en esta necesidad.")
        else:
            st.dataframe(propios[["nombre", "decision_deportiva", "riesgo_continuidad", "rol_proxima_temporada", "score_modelo", "conclusion"]], use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Candidatos")
        candidatos = need["candidatos"]
        if candidatos.empty:
            st.warning("No hay candidatos cargados.")
        else:
            st.dataframe(candidatos[["nombre", "equipo", "posicion_principal", "decision_deportiva", "score_modelo", "rol_ideal", "conclusion"]], use_container_width=True, hide_index=True)
            add_name = st.selectbox("Añadir a shortlist", candidatos["nombre"].tolist(), key=f"short_{selected_need}")
            nota = st.text_input("Nota shortlist", value=f"Candidato para {selected_need}", key=f"nota_{selected_need}")
            if st.button("Añadir candidato", key=f"add_{selected_need}"):
                r = candidatos[candidatos["nombre"] == add_name].iloc[0]
                new = pd.DataFrame([{"nombre": r["nombre"], "equipo": r["equipo"], "posicion_principal": r["posicion_principal"], "score_modelo": r["score_modelo"], "decision_deportiva": r["decision_deportiva"], "necesidad": selected_need, "nota_shortlist": nota}])
                st.session_state.shortlist = pd.concat([st.session_state.shortlist, new], ignore_index=True).drop_duplicates(subset=["nombre", "necesidad"], keep="last")
                st.success(f"{add_name} añadido a shortlist.")
    st.subheader("Shortlist")
    if st.session_state.shortlist.empty:
        st.info("Todavía no hay candidatos guardados.")
    else:
        st.dataframe(st.session_state.shortlist.sort_values("score_modelo", ascending=False), use_container_width=True, hide_index=True)

with tabs[4]:
    st.header("Comparador avanzado")
    if ojeados.empty:
        st.warning("No hay jugadores ojeados.")
    else:
        c1, c2 = st.columns(2)
        propio_name = c1.selectbox("Jugador propio", jugadores["nombre"].tolist())
        ojeado_name = c2.selectbox("Jugador ojeado", ojeados["nombre"].tolist())
        propio = jugadores[jugadores["nombre"] == propio_name].iloc[0]
        ojeado = ojeados[ojeados["nombre"] == ojeado_name].iloc[0]
        comp = pd.DataFrame({"Métrica": [NOMBRES.get(c, c) for c in ENCAJES], propio["nombre"]: [float(propio[c]) for c in ENCAJES], ojeado["nombre"]: [float(ojeado[c]) for c in ENCAJES], "Diferencia": [round(float(ojeado[c]) - float(propio[c]), 2) for c in ENCAJES]})
        cc1, cc2 = st.columns([1, 1])
        cc1.dataframe(comp, use_container_width=True, hide_index=True)
        cc2.bar_chart(comp.set_index("Métrica")[[propio["nombre"], ojeado["nombre"]]])
        delta = float(ojeado["score_modelo"]) - float(propio["score_modelo"])
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Score {propio['nombre']}", f"{float(propio['score_modelo']):.2f}")
        m2.metric(f"Score {ojeado['nombre']}", f"{float(ojeado['score_modelo']):.2f}")
        m3.metric("Diferencia", f"{delta:+.2f}")
        if delta > 0.5:
            st.success(f"{ojeado['nombre']} mejora claramente a {propio['nombre']} en el modelo ponderado.")
        elif delta < -0.5:
            st.warning(f"{ojeado['nombre']} no mejora a {propio['nombre']} con los pesos actuales.")
        else:
            st.info("Perfiles de valor parecido. Decide por rol, coste, disponibilidad y contexto.")

with tabs[5]:
    st.header("Ficha de jugador")
    fuente = st.radio("Fuente", ["Plantilla propia", "Ojeo", "Todos"], horizontal=True)
    base_df = jugadores if fuente == "Plantilla propia" else ojeados if fuente == "Ojeo" else todos
    if base_df.empty:
        st.warning("No hay datos.")
    else:
        nombre = st.selectbox("Seleccionar jugador", base_df["nombre"].tolist())
        ficha(base_df, nombre)

with tabs[6]:
    st.header("Modelo y score ponderado")
    st.subheader("Principios del modelo Noname")
    model_cols = st.columns(4)
    for idx, (title, text) in enumerate(MODELO):
        with model_cols[idx % 4]:
            st.markdown(f'<div class="card-tight"><div style="font-weight:900;">{esc(title)}</div><div class="small" style="margin-top:5px;">{esc(text)}</div></div>', unsafe_allow_html=True)
    st.subheader("Ranking por score ponderado")
    c1, c2 = st.columns(2)
    fuente_rank = c1.radio("Fuente ranking", ["Propios", "Ojeados", "Todos"], horizontal=True)
    posicion_rank = c2.selectbox("Filtro posición", ["Todas"] + POSICIONES)
    rank_df = jugadores if fuente_rank == "Propios" else ojeados if fuente_rank == "Ojeados" else todos
    if posicion_rank != "Todas":
        rank_df = by_pos(rank_df, [posicion_rank])
    rank_df = rank_df.sort_values("score_modelo", ascending=False)
    st.dataframe(rank_df[["nombre", "equipo", "tipo", "posicion_principal", "decision_deportiva", "score_modelo", "encaje_modelo_general", "rol_proxima_temporada"]], use_container_width=True, hide_index=True)
    st.bar_chart(rank_df.set_index("nombre")["score_modelo"])

with tabs[7]:
    st.header("Exportar")
    st.download_button("Descargar plantilla propia CSV editada", csv_bytes(jugadores.drop(columns=["score_modelo"], errors="ignore")), "jugadores_noname_export.csv", "text/csv")
    st.download_button("Descargar lista de ojeo CSV editada", csv_bytes(ojeados.drop(columns=["score_modelo"], errors="ignore")), "jugadores_ojeados_noname_export.csv", "text/csv")
    st.download_button("Descargar base unificada con score", csv_bytes(todos), "jugadores_total_noname_export.csv", "text/csv")
    st.download_button("Descargar shortlist", csv_bytes(st.session_state.shortlist), "shortlist_noname.csv", "text/csv")
    st.subheader("Archivos esperados en GitHub")
    st.code("streamlit_app.py\nrequirements.txt\njugadores_noname.csv\njugadores_ojeados_noname.csv")