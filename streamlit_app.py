import html
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURACIÓN
# =========================================================

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

DECISION_ORDER = [
    "Renovar",
    "Renovar con rol secundario",
    "Duda",
    "Pendiente de evaluación",
    "No ofrecer renovación",
]

DECISION_COLORS = {
    "Renovar": "#16A34A",
    "Renovar con rol secundario": "#2563EB",
    "Duda": "#D97706",
    "Pendiente de evaluación": "#7C3AED",
    "No ofrecer renovación": "#DC2626",
    "Objetivo mercado": "#0EA5E9",
    "Seguimiento": "#64748B",
    "Descartar": "#111827",
}

POSICIONES = ["POR", "LD", "LI", "DFC", "MCD", "MC", "MCO", "ED", "EI", "DC"]

BLOQUES_POSICION = {
    "Portería": ["POR"],
    "Lateral derecho": ["LD"],
    "Lateral izquierdo": ["LI"],
    "Centrales": ["DFC"],
    "Mediocentro / pivote": ["MCD", "MC"],
    "Mediapunta": ["MCO"],
    "Extremos": ["ED", "EI"],
    "Delanteros": ["DC"],
}

NECESIDADES_BASE = [
    {
        "necesidad": "Portero titular",
        "posiciones": ["POR"],
        "motivo": "La estructura actual deja dudas importantes en portería y obliga a priorizar un titular fiable.",
    },
    {
        "necesidad": "Lateral derecho",
        "posiciones": ["LD"],
        "motivo": "Medu y Ángel Santiago no deben computar como soluciones de continuidad.",
    },
    {
        "necesidad": "Recambio lateral izquierdo",
        "posiciones": ["LI", "EI"],
        "motivo": "Raúl Crespo es estructural, pero necesita recambio para no jugarlo todo.",
    },
    {
        "necesidad": "Central de rotación",
        "posiciones": ["DFC", "LD"],
        "motivo": "Amine-Asiel son estructurales, pero hace falta rotación fiable/correctora.",
    },
    {
        "necesidad": "Mediocentro con pie",
        "posiciones": ["MC", "MCD"],
        "motivo": "Bogajo aporta mucho si está, pero la planificación no puede depender solo de su disponibilidad.",
    },
    {
        "necesidad": "6 competitivo",
        "posiciones": ["MCD", "MC"],
        "motivo": "Mati sostiene el equipo, pero necesita competencia y/o complemento con más pie.",
    },
    {
        "necesidad": "Extremo intenso",
        "posiciones": ["ED", "EI"],
        "motivo": "Las bandas tienen talento, pero también dudas de presión, físico, amplitud y continuidad.",
    },
    {
        "necesidad": "Delantero referencia",
        "posiciones": ["DC"],
        "motivo": "La posición de 9 debe reconstruirse: fijación, descarga, área y presión coordinada.",
    },
]

MODELO_NONAME = [
    ("Sistema base", "4-2-3-1 interpretado como 4-4-2 con mediapunta / segundo punta libre."),
    ("Alternativa", "3-4-3 con carriles altos y cuadrado interior."),
    ("Salida", "Salida de 4, laterales asimétricos: uno largo y otro corto/interior."),
    ("Amplitud", "Extremos abiertos. Si uno viene dentro, el lado contrario debe conservar amplitud."),
    ("Presión", "Bloque alto iniciado por delantero + mediapunta. Cerrar dentro y forzar fuera."),
    ("Transición ofensiva", "Vertical tras robo, buscando mediapunta libre, delantero o espacio."),
    ("Transición defensiva", "Presión tras pérdida; si se supera, embudo interior y reorganización."),
    ("Rest-defence", "3+2 o 3+1 según altura de pivotes y laterales."),
]

SLOTS_4231 = [
    ("POR", 50, 90),
    ("LI", 18, 73), ("DFC", 38, 76), ("DFC", 62, 76), ("LD", 82, 73),
    ("MCD", 40, 58), ("MC", 60, 58),
    ("EI", 18, 39), ("MCO", 50, 39), ("ED", 82, 39),
    ("DC", 50, 18),
]

SLOTS_343 = [
    ("POR", 50, 90),
    ("DFC", 28, 76), ("DFC", 50, 78), ("DFC", 72, 76),
    ("LI", 15, 55), ("MCD", 40, 56), ("MC", 60, 56), ("LD", 85, 55),
    ("MCO", 40, 34), ("MCO", 60, 34),
    ("DC", 50, 18),
]

MAPEO_SLOTS = {
    "POR": ["POR"],
    "LD": ["LD", "DFC"],
    "LI": ["LI", "EI"],
    "DFC": ["DFC", "LD", "LI"],
    "MCD": ["MCD", "MC"],
    "MC": ["MC", "MCD", "MCO"],
    "MCO": ["MCO", "DC", "ED", "EI", "MC"],
    "ED": ["ED", "EI", "MCO", "DC"],
    "EI": ["EI", "ED", "MCO", "DC"],
    "DC": ["DC", "MCO", "EI", "ED"],
}


# =========================================================
# ESTILO Y UTILIDADES
# =========================================================

def css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);
            color: #0F172A;
        }
        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        h1, h2, h3, h4 {
            color: #0F172A !important;
            letter-spacing: -0.02em;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(15,23,42,.06);
        }
        .hero {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 55%, #0EA5E9 100%);
            color: white;
            border-radius: 24px;
            padding: 26px 30px;
            margin-bottom: 18px;
            box-shadow: 0 16px 40px rgba(15,23,42,.20);
        }
        .hero h1 {
            color: white !important;
            margin: 0;
            font-size: 34px;
        }
        .hero p {
            color: #DBEAFE;
            margin: 8px 0 0 0;
            font-size: 15px;
        }
        .card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(15,23,42,.06);
        }
        .card-tight {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 12px;
            margin-bottom: 10px;
            box-shadow: 0 4px 14px rgba(15,23,42,.05);
        }
        .section-title {
            font-weight: 800;
            font-size: 17px;
            margin-bottom: 8px;
        }
        .small {
            font-size: 12px;
            color: #64748B;
        }
        .pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            margin: 2px 4px 2px 0;
            color: white;
        }
        .need {
            border-left: 5px solid #2563EB;
            padding: 12px 14px;
            background: #FFFFFF;
            border-radius: 14px;
            margin-bottom: 10px;
            box-shadow: 0 4px 14px rgba(15,23,42,.05);
        }
        .need-title {
            font-weight: 800;
            font-size: 15px;
        }
        .need-text {
            color: #475569;
            font-size: 13px;
            margin-top: 3px;
        }
        .pitch {
            position: relative;
            height: 660px;
            border-radius: 24px;
            overflow: hidden;
            border: 4px solid #D9F99D;
            background:
                linear-gradient(90deg, rgba(255,255,255,.09) 0 1px, transparent 1px 100%),
                repeating-linear-gradient(90deg, #15803D 0 10%, #16A34A 10% 20%);
            box-shadow: inset 0 0 0 2px rgba(255,255,255,.45), 0 18px 40px rgba(15,23,42,.16);
        }
        .pitch::before {
            content: "";
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 2px;
            background: rgba(255,255,255,.65);
        }
        .circle {
            position: absolute;
            left: calc(50% - 62px);
            top: calc(50% - 62px);
            width: 124px;
            height: 124px;
            border: 2px solid rgba(255,255,255,.65);
            border-radius: 50%;
        }
        .box-top, .box-bottom {
            position: absolute;
            left: 23%;
            width: 54%;
            height: 18%;
            border: 2px solid rgba(255,255,255,.65);
        }
        .box-top { top: 8%; }
        .box-bottom { bottom: 8%; }
        .player-dot {
            position: absolute;
            width: 142px;
            min-height: 72px;
            transform: translate(-71px, -36px);
            background: rgba(255,255,255,.96);
            border: 2px solid #0F172A;
            border-radius: 16px;
            text-align: center;
            padding: 10px 7px;
            box-shadow: 0 8px 22px rgba(15,23,42,.22);
            color: #0F172A;
        }
        .player-score {
            position: absolute;
            top: -17px;
            left: 50%;
            transform: translateX(-50%);
            width: 36px;
            height: 36px;
            line-height: 32px;
            border-radius: 999px;
            color: white;
            font-weight: 900;
            font-size: 12px;
            border: 2px solid white;
        }
        .player-name {
            margin-top: 7px;
            font-weight: 900;
            font-size: 13px;
            line-height: 1.1;
        }
        .player-role {
            color: #64748B;
            font-size: 10px;
            margin-top: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .slot {
            color: #B45309;
            font-weight: 800;
            font-size: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def e(value) -> str:
    return html.escape("" if pd.isna(value) else str(value))


def read_csv(uploaded, default_path: str) -> pd.DataFrame:
    if uploaded is not None:
        return pd.read_csv(uploaded, encoding="utf-8-sig")
    if Path(default_path).exists():
        return pd.read_csv(default_path, encoding="utf-8-sig")
    return pd.DataFrame()


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
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
    if "tipo" not in df.columns:
        df["tipo"] = ""
    return df


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def decision_label(decision: str) -> str:
    icons = {
        "Renovar": "🟢 Renovar",
        "Renovar con rol secundario": "🔵 Rol secundario",
        "Duda": "🟡 Duda",
        "Pendiente de evaluación": "🟣 Pendiente",
        "No ofrecer renovación": "🔴 No renovar",
        "Objetivo mercado": "⭐ Objetivo",
        "Seguimiento": "👁️ Seguimiento",
        "Descartar": "⚫ Descartar",
    }
    return icons.get(decision, decision)


def color_decision(decision: str) -> str:
    return DECISION_COLORS.get(decision, "#64748B")


def normalize_position(pos: str) -> list[str]:
    pos = str(pos or "").upper().strip()
    if not pos:
        return []
    parts = []
    for raw in pos.replace("-", "/").split("/"):
        raw = raw.strip()
        if raw:
            parts.append(raw)
    return parts


def has_position(row, allowed: list[str]) -> bool:
    positions = normalize_position(row.get("posicion_principal", "")) + normalize_position(row.get("posicion_secundaria", ""))
    return any(p in allowed for p in positions)


def filter_by_positions(df: pd.DataFrame, allowed: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df.apply(lambda r: has_position(r, allowed), axis=1)].copy()


def decision_counts(df: pd.DataFrame) -> dict:
    if df.empty or "decision_deportiva" not in df.columns:
        return {}
    counts = df["decision_deportiva"].value_counts().to_dict()
    return {k: counts.get(k, 0) for k in DECISION_ORDER if counts.get(k, 0)}


def top_players(df: pd.DataFrame, n=5) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values("encaje_modelo_general", ascending=False).head(n)


def pick_xi(df: pd.DataFrame, slots: list[tuple[str, int, int]], fuente: str) -> list[dict]:
    data = df.copy()
    if fuente == "Solo propios":
        data = data[data["tipo"].str.lower().isin(["propio"])]
    elif fuente == "Solo ojeados":
        data = data[data["tipo"].str.lower().isin(["ojeado", "mercado", "rival", "recambio"])]
    elif fuente == "Propios renovables":
        data = data[data["decision_deportiva"].isin(["Renovar", "Renovar con rol secundario", "Duda", "Pendiente de evaluación"])]

    used = set()
    output = []

    for slot, x, y in slots:
        allowed = MAPEO_SLOTS.get(slot, [slot])
        candidates = data[~data["nombre"].isin(used)].copy()
        candidates = filter_by_positions(candidates, allowed)
        if candidates.empty:
            output.append(
                {
                    "slot": slot,
                    "x": x,
                    "y": y,
                    "nombre": "VACANTE",
                    "score": 0,
                    "decision": "Vacante",
                    "rol": "Necesidad de mercado",
                    "equipo": "",
                }
            )
            continue

        # Pequeño bonus por coincidencia exacta en posición principal.
        def slot_score(r):
            base = float(r.get("encaje_modelo_general", 0))
            posiciones = normalize_position(r.get("posicion_principal", "")) + normalize_position(r.get("posicion_secundaria", ""))
            if slot in posiciones:
                base += 0.35
            return base

        candidates["_slot_score"] = candidates.apply(slot_score, axis=1)
        pick = candidates.sort_values(["_slot_score", "encaje_modelo_general"], ascending=False).iloc[0]
        used.add(pick["nombre"])

        output.append(
            {
                "slot": slot,
                "x": x,
                "y": y,
                "nombre": pick.get("nombre", ""),
                "score": float(pick.get("encaje_modelo_general", 0)),
                "decision": pick.get("decision_deportiva", ""),
                "rol": pick.get("rol_proxima_temporada", "") or pick.get("rol_ideal", ""),
                "equipo": pick.get("equipo", ""),
            }
        )

    return output


def render_pitch(players: list[dict]) -> str:
    html_parts = [
        '<div class="pitch">',
        '<div class="circle"></div>',
        '<div class="box-top"></div>',
        '<div class="box-bottom"></div>',
    ]

    for p in players:
        decision = p["decision"]
        color = "#334155" if decision == "Vacante" else color_decision(decision)
        score = "--" if p["score"] <= 0 else f"{p['score']:.1f}"
        html_parts.append(
            f"""
            <div class="player-dot" style="left:{p['x']}%; top:{p['y']}%; border-color:{color};">
                <div class="player-score" style="background:{color};">{score}</div>
                <div class="player-name">{e(p['nombre'])}</div>
                <div class="slot">{e(p['slot'])} · {e(p['equipo'])}</div>
                <div class="player-role">{e(p['rol'])}</div>
            </div>
            """
        )

    html_parts.append("</div>")
    return "\n".join(html_parts)


def market_needs(jugadores: pd.DataFrame, ojeados: pd.DataFrame) -> list[dict]:
    needs = []
    for n in NECESIDADES_BASE:
        candidatos = filter_by_positions(ojeados, n["posiciones"])
        candidatos = candidatos[candidatos["decision_deportiva"].isin(["Objetivo mercado", "Seguimiento", "Pendiente de evaluación", ""])]
        candidatos = candidatos.sort_values("encaje_modelo_general", ascending=False)

        propios_pos = filter_by_positions(jugadores, n["posiciones"])
        riesgo = propios_pos[propios_pos["decision_deportiva"].isin(["No ofrecer renovación", "Duda", "Pendiente de evaluación"])]
        prioridad = "Alta" if len(riesgo) >= 1 or len(candidatos) == 0 else "Media"

        needs.append(
            {
                "necesidad": n["necesidad"],
                "posiciones": ", ".join(n["posiciones"]),
                "motivo": n["motivo"],
                "prioridad": prioridad,
                "candidatos": candidatos,
                "propios": propios_pos,
            }
        )
    return needs


def metric_badge(label: str, value: int | float, color="#2563EB") -> str:
    return f"""
    <div class="card-tight">
        <div class="small">{e(label)}</div>
        <div style="font-size:28px;font-weight:900;color:{color};">{value}</div>
    </div>
    """


def player_card(row: pd.Series, compact=False) -> str:
    decision = row.get("decision_deportiva", "")
    color = color_decision(decision)
    score = float(row.get("encaje_modelo_general", 0))
    content = f"""
    <div class="card-tight" style="border-left:5px solid {color};">
        <div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start;">
            <div>
                <div style="font-weight:900;font-size:16px;">{e(row.get('nombre',''))}</div>
                <div class="small">{e(row.get('equipo',''))} · {e(row.get('posicion_principal',''))} · {e(row.get('rol_ideal','') or row.get('rol_actual',''))}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:24px;font-weight:900;color:{color};">{score:.1f}</div>
                <div class="small">encaje</div>
            </div>
        </div>
        <div style="margin-top:8px;">
            <span class="pill" style="background:{color};">{e(decision_label(decision))}</span>
        </div>
    """
    if not compact:
        content += f"""
        <div class="small" style="margin-top:8px;">{e(row.get('conclusion',''))}</div>
        """
    content += "</div>"
    return content


def ficha_jugador(df: pd.DataFrame, nombre: str) -> None:
    row = df[df["nombre"] == nombre].iloc[0]
    st.markdown(
        f"""
        <div class="card" style="border-left:6px solid {color_decision(row.get('decision_deportiva',''))};">
            <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;">
                <div>
                    <div class="small">{e(row.get('tipo',''))} · {e(row.get('equipo',''))}</div>
                    <h2 style="margin:0;">{e(row.get('nombre',''))}</h2>
                    <div class="small">{e(row.get('nombre_oficial',''))}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:36px;font-weight:900;color:{color_decision(row.get('decision_deportiva',''))};">{float(row.get('encaje_modelo_general',0)):.1f}</div>
                    <div class="small">encaje general</div>
                </div>
            </div>
            <div style="margin-top:12px;">
                <span class="pill" style="background:{color_decision(row.get('decision_deportiva',''))};">{e(decision_label(row.get('decision_deportiva','')))}</span>
                <span class="pill" style="background:#0F172A;">{e(row.get('posicion_principal',''))}</span>
                <span class="pill" style="background:#64748B;">Riesgo: {e(row.get('riesgo_continuidad',''))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(metric_badge("Rol actual", row.get("rol_actual", "") or "—", "#0F172A"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_badge("Rol ideal", row.get("rol_ideal", "") or "—", "#0F172A"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_badge("Rol próxima temporada", row.get("rol_proxima_temporada", "") or "—", "#0F172A"), unsafe_allow_html=True)

    col1, col2 = st.columns([1.15, 1])
    with col1:
        enc_cols = [c for c in ENCAJES if c in df.columns]
        enc = pd.DataFrame(
            {
                "Encaje": [NOMBRES_ENCAJE.get(c, c) for c in enc_cols],
                "Valor": [float(row.get(c, 0)) for c in enc_cols],
            }
        ).set_index("Encaje")
        st.subheader("Mapa de encaje")
        st.bar_chart(enc)

    with col2:
        st.subheader("Lectura rápida")
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title">Fortalezas</div>
                <div class="small">{e(row.get('fortalezas',''))}</div>
                <hr>
                <div class="section-title">Debilidades</div>
                <div class="small">{e(row.get('debilidades',''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title">Dónde rinde</div>
                <div class="small">{e(row.get('contexto_donde_rinde',''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title">Dónde sufre</div>
                <div class="small">{e(row.get('contexto_donde_sufre',''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Observación táctica")
    st.info(row.get("observacion_tactica", ""))

    st.subheader("Conclusión")
    st.write(row.get("conclusion", ""))


# =========================================================
# CARGA
# =========================================================

css()

st.sidebar.title("Heras MatchLab")
st.sidebar.caption("Planificación + ojeo | Noname")
st.sidebar.markdown("---")

uploaded_jug = st.sidebar.file_uploader("Subir jugadores_noname.csv", type=["csv"])
uploaded_ojeados = st.sidebar.file_uploader("Subir jugadores_ojeados_noname.csv", type=["csv"])

jugadores = clean_df(read_csv(uploaded_jug, JUGADORES_CSV))
ojeados = clean_df(read_csv(uploaded_ojeados, OJEADOS_CSV))

if jugadores.empty:
    st.error("No se encontró `jugadores_noname.csv`. Súbelo desde la barra lateral o colócalo en la raíz del repositorio.")
    st.stop()

if ojeados.empty:
    st.warning("No se encontró `jugadores_ojeados_noname.csv`. La app funcionará solo con plantilla propia.")
    ojeados = pd.DataFrame(columns=jugadores.columns)

for col in jugadores.columns:
    if col not in ojeados.columns:
        ojeados[col] = ""
for col in ojeados.columns:
    if col not in jugadores.columns:
        jugadores[col] = ""
ojeados = ojeados[jugadores.columns]
todos = pd.concat([jugadores, ojeados], ignore_index=True)

# =========================================================
# CABECERA
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>Heras MatchLab · Noname</h1>
        <p>Planificación de plantilla, mapa visual por posiciones y lista de ojeo conectada al modelo de juego.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        "🏠 Dashboard",
        "🧩 Campograma",
        "📋 Plantilla",
        "👁️ Ojeo / Mercado",
        "🔁 Comparador",
        "👤 Ficha",
        "🧠 Modelo",
        "📤 Exportar",
    ]
)

# =========================================================
# DASHBOARD
# =========================================================

with tabs[0]:
    st.header("Dashboard de planificación")

    counts = decision_counts(jugadores)
    total_propios = len(jugadores)
    total_ojeados = len(ojeados)
    renovar = counts.get("Renovar", 0)
    secundarios = counts.get("Renovar con rol secundario", 0)
    dudas = counts.get("Duda", 0) + counts.get("Pendiente de evaluación", 0)
    bajas = counts.get("No ofrecer renovación", 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Plantilla", total_propios)
    c2.metric("Ojeados", total_ojeados)
    c3.metric("Continuidad clara", renovar)
    c4.metric("Dudas / pendientes", dudas)
    c5.metric("No continúan", bajas)

    st.subheader("Estado por bloques de plantilla")
    block_cols = st.columns(4)
    for idx, (bloque, posiciones) in enumerate(BLOQUES_POSICION.items()):
        subset = filter_by_positions(jugadores, posiciones)
        renovables = subset[subset["decision_deportiva"].isin(["Renovar", "Renovar con rol secundario"])]
        problemas = subset[subset["decision_deportiva"].isin(["Duda", "Pendiente de evaluación", "No ofrecer renovación"])]

        with block_cols[idx % 4]:
            ratio = f"{len(renovables)}/{len(subset)}" if len(subset) else "0/0"
            st.markdown(
                f"""
                <div class="card-tight">
                    <div class="small">{e(bloque)}</div>
                    <div style="font-size:26px;font-weight:900;">{ratio}</div>
                    <div class="small">continuidad clara / total</div>
                    <div style="margin-top:8px;">
                        <span class="pill" style="background:#16A34A;">OK {len(renovables)}</span>
                        <span class="pill" style="background:#DC2626;">Riesgo {len(problemas)}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    col1, col2 = st.columns([1.15, 1])
    with col1:
        st.subheader("Prioridades de mercado")
        for need in market_needs(jugadores, ojeados):
            candidatos = need["candidatos"]
            top = "Sin candidato cargado"
            if not candidatos.empty:
                top_row = candidatos.iloc[0]
                top = f"{top_row['nombre']} · {top_row['equipo']} · {float(top_row['encaje_modelo_general']):.1f}"
            color = "#DC2626" if need["prioridad"] == "Alta" else "#2563EB"
            st.markdown(
                f"""
                <div class="need" style="border-left-color:{color};">
                    <div class="need-title">{e(need['necesidad'])} · {e(need['prioridad'])}</div>
                    <div class="need-text">{e(need['motivo'])}</div>
                    <div class="small" style="margin-top:6px;"><b>Mejor ojeado:</b> {e(top)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader("Mejores encajes de la plantilla")
        for _, r in top_players(jugadores, 6).iterrows():
            st.markdown(player_card(r, compact=True), unsafe_allow_html=True)

# =========================================================
# CAMPOGRAMA
# =========================================================

with tabs[1]:
    st.header("Campograma y mapa visual")

    c1, c2, c3 = st.columns(3)
    with c1:
        estructura = st.selectbox("Estructura", ["4-2-3-1 / 4-4-2", "3-4-3"])
    with c2:
        fuente_xi = st.selectbox("Fuente", ["Propios renovables", "Solo propios", "Solo ojeados", "Todos"])
    with c3:
        metrica_visual = st.selectbox("Orden visual", ["encaje_modelo_general", "encaje_4231_442", "encaje_343"], format_func=lambda x: NOMBRES_ENCAJE.get(x, x))

    slots = SLOTS_4231 if estructura == "4-2-3-1 / 4-4-2" else SLOTS_343
    # Para el campograma se usa encaje_modelo_general de base. La métrica visual afecta al ranking lateral.
    xi = pick_xi(todos, slots, fuente_xi)

    col1, col2 = st.columns([1.35, 1])
    with col1:
        st.markdown(render_pitch(xi), unsafe_allow_html=True)

    with col2:
        st.subheader("Lectura de posiciones")
        xi_df = pd.DataFrame(xi)
        st.dataframe(
            xi_df[["slot", "nombre", "equipo", "score", "decision", "rol"]],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Ranking por posición")
        pos_select = st.selectbox("Ver posición", POSICIONES, index=POSICIONES.index("DC"))
        pos_df = filter_by_positions(todos, [pos_select]).sort_values(metrica_visual, ascending=False)
        cols = ["nombre", "equipo", "tipo", "decision_deportiva", metrica_visual, "rol_proxima_temporada"]
        cols = [c for c in cols if c in pos_df.columns]
        st.dataframe(pos_df[cols], use_container_width=True, hide_index=True)

# =========================================================
# PLANTILLA
# =========================================================

with tabs[2]:
    st.header("Plantilla propia")

    f1, f2, f3 = st.columns(3)
    with f1:
        pos_filter = st.multiselect("Posición", sorted(jugadores["posicion_principal"].unique().tolist()), default=sorted(jugadores["posicion_principal"].unique().tolist()))
    with f2:
        dec_filter = st.multiselect("Decisión", sorted(jugadores["decision_deportiva"].unique().tolist()), default=sorted(jugadores["decision_deportiva"].unique().tolist()))
    with f3:
        riesgo_filter = st.multiselect("Riesgo", sorted(jugadores["riesgo_continuidad"].unique().tolist()), default=sorted(jugadores["riesgo_continuidad"].unique().tolist()))

    data = jugadores[
        jugadores["posicion_principal"].isin(pos_filter)
        & jugadores["decision_deportiva"].isin(dec_filter)
        & jugadores["riesgo_continuidad"].isin(riesgo_filter)
    ].copy()

    st.subheader("Vista ejecutiva")
    cols = [
        "nombre",
        "posicion_principal",
        "decision_deportiva",
        "prioridad_renovacion",
        "riesgo_continuidad",
        "rol_proxima_temporada",
        "encaje_modelo_general",
        "conclusion",
    ]
    st.dataframe(data[cols], use_container_width=True, hide_index=True)

    st.subheader("Tarjetas rápidas")
    card_cols = st.columns(3)
    for idx, (_, r) in enumerate(data.sort_values("encaje_modelo_general", ascending=False).iterrows()):
        with card_cols[idx % 3]:
            st.markdown(player_card(r), unsafe_allow_html=True)

# =========================================================
# OJEO / MERCADO
# =========================================================

with tabs[3]:
    st.header("Ojeo / Mercado")

    st.info("Los jugadores actuales de la lista de ojeo son ficticios. Los iremos sustituyendo por rivales reales mediante entrevistas como hicimos con la plantilla propia.")

    needs = market_needs(jugadores, ojeados)
    need_names = [n["necesidad"] for n in needs]
    selected_need = st.selectbox("Necesidad de mercado", need_names)
    need = next(n for n in needs if n["necesidad"] == selected_need)

    st.markdown(
        f"""
        <div class="card">
            <div class="small">Prioridad: {e(need['prioridad'])} · Posiciones: {e(need['posiciones'])}</div>
            <h3 style="margin:4px 0 8px 0;">{e(need['necesidad'])}</h3>
            <div>{e(need['motivo'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Situación interna")
        propios = need["propios"].sort_values("encaje_modelo_general", ascending=False)
        if propios.empty:
            st.warning("No hay jugadores propios en esta posición.")
        else:
            st.dataframe(
                propios[
                    [
                        "nombre",
                        "decision_deportiva",
                        "riesgo_continuidad",
                        "rol_proxima_temporada",
                        "encaje_modelo_general",
                        "conclusion",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    with col2:
        st.subheader("Candidatos ojeados")
        candidatos = need["candidatos"]
        if candidatos.empty:
            st.warning("No hay candidatos ojeados cargados para esta necesidad.")
        else:
            st.dataframe(
                candidatos[
                    [
                        "nombre",
                        "equipo",
                        "posicion_principal",
                        "decision_deportiva",
                        "encaje_modelo_general",
                        "rol_ideal",
                        "conclusion",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    st.subheader("Lista completa de ojeo")
    if ojeados.empty:
        st.warning("No hay lista de ojeo cargada.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            pos_o = st.multiselect("Posición ojeada", sorted(ojeados["posicion_principal"].unique().tolist()), default=sorted(ojeados["posicion_principal"].unique().tolist()))
        with f2:
            equipo_o = st.multiselect("Equipo rival", sorted(ojeados["equipo"].unique().tolist()), default=sorted(ojeados["equipo"].unique().tolist()))
        with f3:
            estado_o = st.multiselect("Estado", sorted(ojeados["decision_deportiva"].unique().tolist()), default=sorted(ojeados["decision_deportiva"].unique().tolist()))

        oj = ojeados[
            ojeados["posicion_principal"].isin(pos_o)
            & ojeados["equipo"].isin(equipo_o)
            & ojeados["decision_deportiva"].isin(estado_o)
        ].copy()

        st.dataframe(
            oj[
                [
                    "id_jugador",
                    "nombre",
                    "equipo",
                    "posicion_principal",
                    "rol_ideal",
                    "decision_deportiva",
                    "prioridad_renovacion",
                    "encaje_modelo_general",
                    "conclusion",
                ]
            ].sort_values("encaje_modelo_general", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

# =========================================================
# COMPARADOR
# =========================================================

with tabs[4]:
    st.header("Comparador propio vs ojeado")

    if ojeados.empty:
        st.warning("No hay jugadores ojeados para comparar.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            propio_name = st.selectbox("Jugador propio", jugadores["nombre"].tolist())
        with c2:
            ojeado_name = st.selectbox("Jugador ojeado", ojeados["nombre"].tolist())

        propio = jugadores[jugadores["nombre"] == propio_name].iloc[0]
        ojeado = ojeados[ojeados["nombre"] == ojeado_name].iloc[0]

        st.markdown(
            f"""
            <div class="card">
                <h3>{e(ojeado_name)} vs {e(propio_name)}</h3>
                <div class="small">Comparación por encaje táctico, no por calidad absoluta.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        comp = pd.DataFrame(
            {
                "Métrica": [NOMBRES_ENCAJE.get(c, c) for c in ENCAJES],
                propio["nombre"]: [float(propio[c]) for c in ENCAJES],
                ojeado["nombre"]: [float(ojeado[c]) for c in ENCAJES],
                "Diferencia ojeado-propio": [round(float(ojeado[c]) - float(propio[c]), 2) for c in ENCAJES],
            }
        )

        cc1, cc2 = st.columns([1, 1])
        with cc1:
            st.dataframe(comp, use_container_width=True, hide_index=True)
        with cc2:
            st.bar_chart(comp.set_index("Métrica")[[propio["nombre"], ojeado["nombre"]]])

        delta = float(ojeado["encaje_modelo_general"]) - float(propio["encaje_modelo_general"])
        if delta > 0.5:
            st.success(f"{ojeado['nombre']} mejora el encaje general respecto a {propio['nombre']} (+{delta:.1f}).")
        elif delta < -0.5:
            st.warning(f"{ojeado['nombre']} no mejora el encaje general de {propio['nombre']} ({delta:.1f}).")
        else:
            st.info("Son perfiles de encaje global parecido. La decisión dependerá de rol, disponibilidad, coste y contexto.")

# =========================================================
# FICHA
# =========================================================

with tabs[5]:
    st.header("Ficha de jugador")

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
        nombre = st.selectbox("Seleccionar jugador", base["nombre"].tolist())
        ficha_jugador(base, nombre)

# =========================================================
# MODELO
# =========================================================

with tabs[6]:
    st.header("Modelo y encaje")

    st.subheader("Principios del modelo Noname")
    model_cols = st.columns(4)
    for idx, (title, text) in enumerate(MODELO_NONAME):
        with model_cols[idx % 4]:
            st.markdown(
                f"""
                <div class="card-tight">
                    <div style="font-weight:900;">{e(title)}</div>
                    <div class="small" style="margin-top:5px;">{e(text)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("Ranking de encaje")
    c1, c2 = st.columns(2)
    with c1:
        fuente_rank = st.radio("Fuente ranking", ["Propios", "Ojeados", "Todos"], horizontal=True)
    with c2:
        metric = st.selectbox("Métrica", ENCAJES, format_func=lambda x: NOMBRES_ENCAJE.get(x, x))

    if fuente_rank == "Propios":
        base_rank = jugadores
    elif fuente_rank == "Ojeados":
        base_rank = ojeados
    else:
        base_rank = todos

    rank = base_rank[["nombre", "equipo", "tipo", "posicion_principal", "decision_deportiva", metric, "rol_proxima_temporada"]].sort_values(metric, ascending=False)
    st.dataframe(rank, use_container_width=True, hide_index=True)
    st.bar_chart(rank.set_index("nombre")[metric])

# =========================================================
# EXPORTAR
# =========================================================

with tabs[7]:
    st.header("Exportar")

    st.download_button("Descargar plantilla propia CSV", csv_bytes(jugadores), "jugadores_noname_export.csv", "text/csv")
    st.download_button("Descargar lista de ojeo CSV", csv_bytes(ojeados), "jugadores_ojeados_noname_export.csv", "text/csv")
    st.download_button("Descargar base unificada CSV", csv_bytes(todos), "jugadores_total_noname_export.csv", "text/csv")

    st.subheader("Archivos esperados en GitHub")
    st.code("""streamlit_app.py
requirements.txt
jugadores_noname.csv
jugadores_ojeados_noname.csv""")