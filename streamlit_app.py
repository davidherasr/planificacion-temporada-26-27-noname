import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Heras MatchLab | Noname",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

JUGADORES_CSV = "jugadores_noname.csv"
OJEADOS_CSV = "jugadores_ojeados_noname.csv"

ENCAJES = [
    "encaje_modelo_general",
    "encaje_4231_442",
    "encaje_343",
    "encaje_presion_alta",
    "encaje_bloque_medio",
    "encaje_salida_balon",
    "encaje_juego_directo_segunda_jugada",
    "encaje_transicion_ofensiva",
    "encaje_transicion_defensiva",
    "encaje_rest_defence",
    "encaje_abp",
]

NOMBRES_ENCAJE = {
    "encaje_modelo_general": "Modelo general",
    "encaje_4231_442": "4-2-3-1 / 4-4-2",
    "encaje_343": "3-4-3",
    "encaje_presion_alta": "Presión alta",
    "encaje_bloque_medio": "Bloque medio",
    "encaje_salida_balon": "Salida de balón",
    "encaje_juego_directo_segunda_jugada": "Juego directo / segunda jugada",
    "encaje_transicion_ofensiva": "Transición ofensiva",
    "encaje_transicion_defensiva": "Transición defensiva",
    "encaje_rest_defence": "Rest-defence",
    "encaje_abp": "ABP",
}

COLUMNAS_DECISION = [
    "id_jugador",
    "nombre",
    "equipo",
    "tipo",
    "posicion_principal",
    "decision_deportiva",
    "prioridad_renovacion",
    "riesgo_continuidad",
    "rol_proxima_temporada",
    "conclusion",
]

MODELO_NONAME = {
    "Sistema nominal": "4-2-3-1",
    "Interpretación real": "4-4-2 con mediapunta / segundo punta libre",
    "Sistema alternativo": "3-4-3 con carriles altos y cuadrado interior",
    "Salida": "Salida de 4. Laterales asimétricos: uno largo y otro corto/interior para proteger pérdida.",
    "Amplitud": "Extremos abiertos. Si uno viene dentro, el lado contrario debe conservar amplitud.",
    "Presión": "Bloque alto. Presión iniciada por delantero + mediapunta.",
    "Orientación": "Cerrar dentro y forzar al rival a jugar hacia fuera.",
    "Transición ofensiva": "Vertical tras robo, buscando mediapunta libre, delantero o espacio.",
    "Transición defensiva": "Presión tras pérdida. Si se supera, embudo interior y reorganización.",
    "Rest-defence": "3+2 o 3+1 según altura de pivotes/laterales.",
}

REGLAS_PRESION = {
    "Salida de 4 + pivote único": {
        "estructura": "4+1",
        "plan": "Delantero va a impares evitando retorno. Mediapunta fija o marca pivote. Si el central receptor queda lejos, salta extremo y línea defensiva ajusta marcas.",
        "objetivo": "Cerrar dentro, impedir que el pivote reciba de cara y forzar fuera o balón largo.",
    },
    "Salida de 4 + doble pivote": {
        "estructura": "4+2",
        "plan": "Delantero y mediapunta van a pares: uno salta y el otro cierra retorno/interior. Extremos orientan y saltan al lateral.",
        "objetivo": "Evitar recepción limpia de los pivotes y obligar a jugar por fuera.",
    },
    "Salida de 3": {
        "estructura": "3+1 / 3+2",
        "plan": "Delantero y mediapunta parten desde dentro. Saltan a centrales cercanos cuando balón va a central exterior. Si conecta con el alejado, salta extremo y hay cambio de marca.",
        "objetivo": "Proteger dentro primero, activar presión al exterior y evitar progresión limpia.",
    },
    "Lateral bajo en salida": {
        "estructura": "4 que se convierte en 3",
        "plan": "Se interpreta como salida de 3 si el lateral baja de forma estable. Si ellos bajan, nosotros podemos subir altura.",
        "objetivo": "No romper estructura por la altura del lateral: orientar, fijar y saltar cuando el balón viaja fuera.",
    },
}

NECESIDADES_BASE = [
    "Portero titular fiable.",
    "Lateral derecho titular o de alto nivel.",
    "Recambio de lateral/carrilero izquierdo para liberar a Raúl Crespo.",
    "Central de rotación fiable, preferiblemente corrector/polivalente.",
    "Mediocentro con pie y pausa.",
    "Pivote/6 de contención que compita con Mati.",
    "Delantero referencia real: fijación, descarga, área y presión coordinada.",
    "Extremo intenso, disciplinado, vertical y trabajador.",
]

def aplicar_estilo(modo):
    if modo == "Oscuro":
        st.markdown("""
        <style>
        .stApp {background:#0B1118;color:#E5E7EB;}
        section[data-testid="stSidebar"] {background:#101923;border-right:1px solid #263241;}
        h1,h2,h3,h4 {color:#F8FAFC !important;}
        [data-testid="stMetric"] {background:#111827;border:1px solid #263241;border-radius:14px;padding:12px;}
        .card {background:#111827;border:1px solid #263241;border-radius:14px;padding:14px;margin-bottom:10px;}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {background:#F7F9FC;color:#111827;}
        section[data-testid="stSidebar"] {background:#FFFFFF;border-right:1px solid #E5E7EB;}
        h1,h2,h3,h4 {color:#0F172A !important;}
        [data-testid="stMetric"] {background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;padding:12px;box-shadow:0 1px 3px rgba(15,23,42,.06);}
        .card {background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;padding:14px;margin-bottom:10px;box-shadow:0 1px 3px rgba(15,23,42,.06);}
        </style>
        """, unsafe_allow_html=True)

def cargar_csv(uploaded, default_path):
    if uploaded is not None:
        return pd.read_csv(uploaded, encoding="utf-8-sig")
    if Path(default_path).exists():
        return pd.read_csv(default_path, encoding="utf-8-sig")
    return pd.DataFrame()

def limpiar(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in ENCAJES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in df.columns:
        if col not in ENCAJES:
            df[col] = df[col].fillna("").astype(str)
    if "decision_deportiva" in df.columns:
        df["decision_deportiva"] = df["decision_deportiva"].replace("", "Pendiente de evaluación")
    return df

def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def decision_icon(decision):
    icons = {
        "Renovar": "🟢 Renovar",
        "Renovar con rol secundario": "🔵 Renovar con rol secundario",
        "Duda": "🟡 Duda",
        "Pendiente de evaluación": "🟣 Pendiente",
        "No ofrecer renovación": "🔴 No ofrecer renovación",
        "Objetivo mercado": "⭐ Objetivo mercado",
        "Seguimiento": "👁️ Seguimiento",
        "Descartar": "⚫ Descartar",
    }
    return icons.get(decision, decision)

def multiselect_col(df, col, label):
    if col not in df.columns:
        return []
    vals = sorted([x for x in df[col].dropna().unique().tolist() if str(x).strip()])
    return st.multiselect(label, vals, default=vals)

def detectar_necesidades(df):
    necesidades = list(NECESIDADES_BASE)
    if "decision_deportiva" in df.columns and "posicion_principal" in df.columns:
        problemas = df[df["decision_deportiva"].isin(["No ofrecer renovación", "Duda", "Pendiente de evaluación"])]
        if len(problemas[problemas["posicion_principal"].str.contains("POR", na=False)]) >= 1:
            necesidades.append("Revisar portería completa: titular + segundo fiable.")
        if len(problemas[problemas["posicion_principal"].str.contains("DC", na=False)]) >= 2:
            necesidades.append("Prioridad máxima: reconstruir la posición de delantero centro.")
        if len(problemas[problemas["posicion_principal"].str.contains("ED|EI", regex=True, na=False)]) >= 2:
            necesidades.append("Añadir al menos un extremo de alta intensidad y disciplina defensiva.")
    out = []
    for n in necesidades:
        if n not in out:
            out.append(n)
    return out

def ficha_jugador(df, nombre):
    row = df[df["nombre"] == nombre].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Posición", row.get("posicion_principal", ""))
    c2.metric("Decisión", row.get("decision_deportiva", ""))
    c3.metric("Prioridad", row.get("prioridad_renovacion", ""))
    c4.metric("Riesgo", row.get("riesgo_continuidad", ""))

    st.markdown(f"""
    <div class="card">
    <h3>{row.get('nombre','')}</h3>
    <b>Equipo:</b> {row.get('equipo','')}<br>
    <b>Nombre oficial:</b> {row.get('nombre_oficial','')}<br>
    <b>Rol actual:</b> {row.get('rol_actual','')}<br>
    <b>Rol ideal:</b> {row.get('rol_ideal','')}<br>
    <b>Rol próxima temporada:</b> {row.get('rol_proxima_temporada','')}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        enc_cols = [c for c in ENCAJES if c in df.columns]
        enc = pd.DataFrame({
            "Encaje": [NOMBRES_ENCAJE.get(c, c) for c in enc_cols],
            "Valor": [float(row[c]) for c in enc_cols],
        }).set_index("Encaje")
        st.subheader("Encajes")
        st.bar_chart(enc)

    with col2:
        st.subheader("Lectura")
        st.write(f"**Fortalezas:** {row.get('fortalezas','')}")
        st.write(f"**Debilidades:** {row.get('debilidades','')}")
        st.write(f"**Dónde rinde:** {row.get('contexto_donde_rinde','')}")
        st.write(f"**Dónde sufre:** {row.get('contexto_donde_sufre','')}")
        st.write(f"**Limitación principal:** {row.get('limitacion_principal','')}")

    st.subheader("Observación táctica")
    st.info(row.get("observacion_tactica", ""))
    st.subheader("Conclusión")
    st.write(row.get("conclusion", ""))

def ranking_table(df, metric):
    cols = ["nombre", "equipo", "tipo", "posicion_principal", "decision_deportiva", metric, "rol_proxima_temporada"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].sort_values(metric, ascending=False)

st.sidebar.title("Heras MatchLab")
st.sidebar.caption("Planificación + ojeo | Noname")

modo = st.sidebar.radio("Modo visual", ["Claro", "Oscuro"], horizontal=True, index=0)
aplicar_estilo(modo)

st.sidebar.markdown("---")
st.sidebar.subheader("Datos")
uploaded_jug = st.sidebar.file_uploader("Subir jugadores_noname.csv", type=["csv"])
uploaded_ojeados = st.sidebar.file_uploader("Subir jugadores_ojeados_noname.csv", type=["csv"])

jugadores = limpiar(cargar_csv(uploaded_jug, JUGADORES_CSV))
ojeados = limpiar(cargar_csv(uploaded_ojeados, OJEADOS_CSV))

if jugadores.empty:
    st.error("No se encontró jugadores_noname.csv. Súbelo desde la barra lateral o ponlo en la raíz del repo.")
    st.stop()

if ojeados.empty:
    st.warning("No se encontró jugadores_ojeados_noname.csv. La app funcionará solo con plantilla propia.")
    ojeados = pd.DataFrame(columns=jugadores.columns)

# Alinear columnas antes de unir
for col in jugadores.columns:
    if col not in ojeados.columns:
        ojeados[col] = ""
for col in ojeados.columns:
    if col not in jugadores.columns:
        jugadores[col] = ""
ojeados = ojeados[jugadores.columns]
todos = pd.concat([jugadores, ojeados], ignore_index=True)

st.title("Heras MatchLab | Planificación + Ojeo Noname")
st.caption("App basada en dos CSV: plantilla propia + lista de ojeo de rivales.")

tabs = st.tabs([
    "📌 Resumen",
    "📋 Plantilla",
    "👁️ Lista de ojeo",
    "🔁 Comparador",
    "👤 Ficha jugador",
    "🧠 Modelo / Encaje",
    "🎯 Mercado",
    "⚙️ Motor presión",
    "📤 Exportar",
])

with tabs[0]:
    st.header("Resumen ejecutivo")

    total_propios = len(jugadores)
    total_ojeados = len(ojeados)

    renovar = int((jugadores["decision_deportiva"] == "Renovar").sum())
    dudas = int((jugadores["decision_deportiva"] == "Duda").sum())
    no_renovar = int((jugadores["decision_deportiva"] == "No ofrecer renovación").sum())
    objetivos = int((ojeados["decision_deportiva"] == "Objetivo mercado").sum()) if not ojeados.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Plantilla propia", total_propios)
    c2.metric("Jugadores ojeados", total_ojeados)
    c3.metric("Renovar", renovar)
    c4.metric("Dudas propias", dudas)
    c5.metric("Objetivos mercado", objetivos)

    col1, col2 = st.columns([1.15, 1])
    with col1:
        st.subheader("Decisiones de plantilla")
        cols = [c for c in COLUMNAS_DECISION if c in jugadores.columns]
        vista = jugadores[cols].copy()
        vista["decision_deportiva"] = vista["decision_deportiva"].apply(decision_icon)
        st.dataframe(vista, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Necesidades principales")
        for n in detectar_necesidades(jugadores)[:9]:
            st.write(f"- {n}")

        st.subheader("Top ojeo por encaje")
        if not ojeados.empty:
            top_ojeo = ojeados.sort_values("encaje_modelo_general", ascending=False).head(6)
            st.dataframe(
                top_ojeo[["nombre", "equipo", "posicion_principal", "decision_deportiva", "encaje_modelo_general"]],
                use_container_width=True,
                hide_index=True,
            )

with tabs[1]:
    st.header("Plantilla propia")

    f1, f2, f3 = st.columns(3)
    with f1:
        pos = multiselect_col(jugadores, "posicion_principal", "Posición")
    with f2:
        decs = multiselect_col(jugadores, "decision_deportiva", "Decisión")
    with f3:
        riesgo = multiselect_col(jugadores, "riesgo_continuidad", "Riesgo")

    data = jugadores.copy()
    if pos:
        data = data[data["posicion_principal"].isin(pos)]
    if decs:
        data = data[data["decision_deportiva"].isin(decs)]
    if riesgo:
        data = data[data["riesgo_continuidad"].isin(riesgo)]

    cols = [c for c in COLUMNAS_DECISION if c in data.columns]
    st.dataframe(data[cols], use_container_width=True, hide_index=True)

with tabs[2]:
    st.header("Lista de ojeo")

    st.info("Los nombres actuales son ficticios. Sustituiremos cada fila por jugadores reales vistos contra nosotros.")

    if ojeados.empty:
        st.warning("No hay jugadores ojeados cargados.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            pos_o = multiselect_col(ojeados, "posicion_principal", "Posición ojeada")
        with f2:
            equipo_o = multiselect_col(ojeados, "equipo", "Equipo rival")
        with f3:
            decision_o = multiselect_col(ojeados, "decision_deportiva", "Estado ojeo")

        oj = ojeados.copy()
        if pos_o:
            oj = oj[oj["posicion_principal"].isin(pos_o)]
        if equipo_o:
            oj = oj[oj["equipo"].isin(equipo_o)]
        if decision_o:
            oj = oj[oj["decision_deportiva"].isin(decision_o)]

        cols = ["id_jugador", "nombre", "equipo", "posicion_principal", "rol_ideal", "decision_deportiva", "prioridad_renovacion", "encaje_modelo_general", "conclusion"]
        cols = [c for c in cols if c in oj.columns]
        st.dataframe(oj[cols].sort_values("encaje_modelo_general", ascending=False), use_container_width=True, hide_index=True)

with tabs[3]:
    st.header("Comparador propio vs ojeado")

    c1, c2 = st.columns(2)
    with c1:
        jugador_propio = st.selectbox("Jugador propio", jugadores["nombre"].tolist())
    with c2:
        if ojeados.empty:
            st.warning("No hay jugadores ojeados para comparar.")
            st.stop()
        jugador_ojeado = st.selectbox("Jugador ojeado", ojeados["nombre"].tolist())

    propio = jugadores[jugadores["nombre"] == jugador_propio].iloc[0]
    externo = ojeados[ojeados["nombre"] == jugador_ojeado].iloc[0]

    comp = pd.DataFrame({
        "Métrica": [NOMBRES_ENCAJE.get(c, c) for c in ENCAJES],
        propio["nombre"]: [float(propio[c]) for c in ENCAJES],
        externo["nombre"]: [float(externo[c]) for c in ENCAJES],
        "Diferencia ojeado-propio": [round(float(externo[c]) - float(propio[c]), 2) for c in ENCAJES],
    })

    cc1, cc2 = st.columns([1, 1])
    with cc1:
        st.dataframe(comp, use_container_width=True, hide_index=True)
    with cc2:
        st.bar_chart(comp.set_index("Métrica")[[propio["nombre"], externo["nombre"]]])

    delta = float(externo["encaje_modelo_general"]) - float(propio["encaje_modelo_general"])
    if delta > 0.5:
        st.success(f"{externo['nombre']} mejora claramente el encaje general respecto a {propio['nombre']} (+{delta:.1f}).")
    elif delta < -0.5:
        st.warning(f"{externo['nombre']} no mejora el encaje general de {propio['nombre']} ({delta:.1f}).")
    else:
        st.info("Son perfiles de encaje global parecido. La decisión dependerá del rol, coste, disponibilidad y contexto.")

with tabs[4]:
    st.header("Ficha jugador")

    fuente = st.radio("Fuente", ["Plantilla propia", "Ojeo", "Todos"], horizontal=True)
    if fuente == "Plantilla propia":
        base = jugadores
    elif fuente == "Ojeo":
        base = ojeados
    else:
        base = todos

    if base.empty:
        st.warning("No hay datos en esta fuente.")
    else:
        nombre = st.selectbox("Jugador", base["nombre"].tolist())
        ficha_jugador(base, nombre)

with tabs[5]:
    st.header("Modelo Noname y rankings de encaje")

    st.subheader("Modelo de juego")
    mcols = st.columns(3)
    for i, (k, v) in enumerate(MODELO_NONAME.items()):
        with mcols[i % 3]:
            st.markdown(f"<div class='card'><b>{k}</b><br>{v}</div>", unsafe_allow_html=True)

    st.subheader("Ranking por métrica")
    fuente_rank = st.radio("Fuente ranking", ["Propios", "Ojeados", "Todos"], horizontal=True)
    if fuente_rank == "Propios":
        base_rank = jugadores
    elif fuente_rank == "Ojeados":
        base_rank = ojeados
    else:
        base_rank = todos

    metric = st.selectbox("Métrica de encaje", [c for c in ENCAJES if c in base_rank.columns], format_func=lambda x: NOMBRES_ENCAJE.get(x, x))
    rank = base_rank[["nombre", "equipo", "tipo", "posicion_principal", "decision_deportiva", metric, "rol_proxima_temporada"]].sort_values(metric, ascending=False)
    st.dataframe(rank, use_container_width=True, hide_index=True)
    st.bar_chart(rank.set_index("nombre")[metric])

with tabs[6]:
    st.header("Mercado")

    st.subheader("Necesidades detectadas desde plantilla propia")
    for n in detectar_necesidades(jugadores):
        st.write(f"- {n}")

    st.subheader("Objetivos ojeados que encajan con necesidades")
    if ojeados.empty:
        st.warning("No hay lista de ojeo cargada.")
    else:
        objetivos = ojeados[ojeados["decision_deportiva"].isin(["Objetivo mercado", "Seguimiento"])].sort_values("encaje_modelo_general", ascending=False)
        cols = ["nombre", "equipo", "posicion_principal", "decision_deportiva", "encaje_modelo_general", "perfil_competencia_necesario", "conclusion"]
        cols = [c for c in cols if c in objetivos.columns]
        st.dataframe(objetivos[cols], use_container_width=True, hide_index=True)

with tabs[7]:
    st.header("Motor de presión según rival")

    c1, c2, c3 = st.columns(3)
    with c1:
        sistema = st.selectbox("Sistema rival", ["4-4-2", "4-3-3", "4-2-3-1", "3-5-2", "3-4-2-1", "5-3-2"])
    with c2:
        salida = st.selectbox("Salida rival", list(REGLAS_PRESION.keys()))
    with c3:
        amenaza = st.selectbox("Amenaza principal", ["Juego directo", "Juego interior", "Banda y centros", "Transición rápida", "Segunda jugada"])

    regla = REGLAS_PRESION[salida]
    st.markdown(f"""
    <div class="card">
    <h3>Plan de presión recomendado</h3>
    <b>Sistema rival:</b> {sistema}<br>
    <b>Estructura:</b> {regla['estructura']}<br><br>
    <b>Ajuste:</b> {regla['plan']}<br><br>
    <b>Objetivo:</b> {regla['objetivo']}<br><br>
    <b>Amenaza principal:</b> {amenaza}
    </div>
    """, unsafe_allow_html=True)

    if amenaza == "Banda y centros":
        st.warning("Prioridad: orientar fuera, pero cerrar zona de remate, segundo palo y rechace.")
    elif amenaza == "Juego interior":
        st.warning("Prioridad: cerrar dentro, impedir pivotes/mediapuntas de cara y forzar pase exterior.")
    elif amenaza == "Transición rápida":
        st.warning("Prioridad: rest-defence estable, lateral corto preparado y pivote en contención.")

with tabs[8]:
    st.header("Exportar")

    st.download_button("Descargar plantilla propia CSV", csv_bytes(jugadores), "jugadores_noname_export.csv", "text/csv")
    st.download_button("Descargar lista de ojeo CSV", csv_bytes(ojeados), "jugadores_ojeados_noname_export.csv", "text/csv")
    st.download_button("Descargar base unificada CSV", csv_bytes(todos), "jugadores_total_noname_export.csv", "text/csv")

    st.subheader("Archivos esperados en GitHub")
    st.code("""streamlit_app.py
requirements.txt
jugadores_noname.csv
jugadores_ojeados_noname.csv""")