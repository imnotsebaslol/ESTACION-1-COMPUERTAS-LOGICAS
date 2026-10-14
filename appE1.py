"""
=====================================================================
 ESTACIÓN 1 – DESBLOQUEA EL CÓDIGO
 Escape room de compuertas lógicas (AND, OR, NOT)
 Ingeniería de Datos e Inteligencia Artificial
---------------------------------------------------------------------
 Ejecutar:
     pip install -r requirements.txt
     streamlit run app.py
=====================================================================
"""

import hashlib
import random
import time

import streamlit as st

# =====================================================================
# 1. CONFIGURACIÓN Y VALORES SECRETOS
# ---------------------------------------------------------------------
# Las respuestas NO se guardan en texto plano: solo se guarda su huella
# SHA-256. Así, aunque alguien lea este archivo en GitHub, no ve el código.
# Lo que escribe el equipo se convierte a SHA-256 y se compara.
# Nunca se imprimen en la interfaz.
# =====================================================================
HASH_CODIGO = "4d13ce97be2042562cd9a3b223786228e12514e68290419cbbfb270e94cb12e5"     # código de los 8 sobres
HASH_RESPUESTA_FINAL = "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"  # resultado del desafío final


def coincide(texto: str, hash_esperado: str) -> bool:
    """True si el texto ingresado corresponde a la respuesta secreta."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest() == hash_esperado

st.set_page_config(
    page_title="Estación 1 · Desbloquea el código",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estado inicial de la estación. Al reiniciar se vuelve exactamente a esto.
ESTADO_INICIAL = {
    "etapa": "inicio",          # inicio | error_codigo | codigo_ok | desafio | error_final | exito
    "codigo_validado": False,   # True solo si el código de 8 dígitos fue correcto
    "final_validado": False,    # True solo si el desafío final fue correcto
    "intentos_codigo": 0,       # intentos fallidos en la capa 1
    "intentos_final": 0,        # intentos fallidos en la capa 2
    "celebrado": False,         # evita lanzar los globos en cada recarga
}


def inicializar_estado() -> None:
    """Crea las variables de st.session_state que falten."""
    for clave, valor in ESTADO_INICIAL.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


# =====================================================================
# 2. NAVEGACIÓN (callbacks de los botones)
# =====================================================================
def ir_a(etapa: str) -> None:
    """Cambia de pantalla."""
    st.session_state.etapa = etapa


def volver_a_inicio() -> None:
    """Regresa a la pantalla del código. Exige volver a validar el código."""
    st.session_state.codigo_validado = False
    st.session_state.final_validado = False
    st.session_state.celebrado = False
    st.session_state.etapa = "inicio"


def volver_al_desafio() -> None:
    """Regresa al desafío final. La bóveda vuelve a quedar bloqueada."""
    st.session_state.final_validado = False
    st.session_state.celebrado = False
    st.session_state.etapa = "desafio"


def reiniciar_estacion() -> None:
    """Borra TODO el progreso (incluidos los campos de texto)."""
    for clave in list(st.session_state.keys()):
        del st.session_state[clave]
    inicializar_estado()


# =====================================================================
# 3. UTILIDADES DE INTERFAZ
# =====================================================================
def html(bloque: str) -> None:
    """Renderiza HTML/CSS. Se compacta en una sola línea para que el
    intérprete de Markdown no lo confunda con bloques de código."""
    limpio = " ".join(l.strip() for l in bloque.strip().splitlines() if l.strip())
    st.markdown(limpio, unsafe_allow_html=True)


def terminal(lineas, clase: str = "", cursor: bool = False) -> str:
    """Devuelve el HTML de una caja tipo terminal."""
    contenido = "".join(f'<div class="t-linea">{l}</div>' for l in lineas)
    if cursor:
        contenido += '<div class="t-linea"><span class="cursor">&gt; </span></div>'
    return f'<div class="terminal {clase}">{contenido}</div>'


def aviso(mensaje: str) -> None:
    """Aviso de validación con el estilo de la app (entrada vacía o inválida)."""
    html(f'<div class="aviso">⚠️ {mensaje}</div>')


def animacion_validacion(mensajes) -> None:
    """Simula el análisis del sistema con una barra de progreso tipo terminal."""
    marco = st.empty()
    total = len(mensajes)
    for i in range(total):
        pct = int((i + 1) / total * 100)
        lineas = "".join(f'<div class="t-linea">&gt; {m}</div>' for m in mensajes[: i + 1])
        marco.markdown(
            f'<div class="terminal">{lineas}'
            f'<div class="barra"><div class="barra-relleno" style="width:{pct}%"></div></div>'
            f'<div class="pct">PROGRESO {pct}%</div></div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.55)
    time.sleep(0.3)


def svg_red_neuronal() -> str:
    """Pequeña red neuronal decorativa dibujada con SVG (sin imágenes externas)."""
    capas_x = [30, 115, 200, 285]
    capas_y = [[25, 65], [15, 45, 75], [28, 62], [45]]
    lineas, nodos = [], []
    for c in range(len(capas_x) - 1):
        for y1 in capas_y[c]:
            for y2 in capas_y[c + 1]:
                lineas.append(
                    f'<line class="sinapsis" x1="{capas_x[c]}" y1="{y1}" '
                    f'x2="{capas_x[c + 1]}" y2="{y2}"/>'
                )
    for c, x in enumerate(capas_x):
        for y in capas_y[c]:
            clase = "neurona salida" if c == len(capas_x) - 1 else "neurona"
            nodos.append(f'<circle class="{clase}" cx="{x}" cy="{y}" r="7"/>')
    return (
        '<svg class="red-neuronal" viewBox="0 0 315 90" xmlns="http://www.w3.org/2000/svg">'
        + "".join(lineas) + "".join(nodos) + "</svg>"
    )


# =====================================================================
# 4. ESTILOS (CSS personalizado)
# =====================================================================
def inyectar_css() -> None:
    html("""
    <style>
    :root{
        --bg:#050816; --panel:rgba(12,19,44,.86);
        --cyan:#22d3ee; --blue:#3b82f6; --purple:#a855f7;
        --green:#22c55e; --red:#ef4444;
        --text:#e2e8f0; --muted:#94a3b8;
        --mono:'Cascadia Code','Consolas','Courier New',monospace;
    }
    /* ---------- Fondo general: degradados + cuadrícula tipo circuito ---------- */
    .stApp{
        background:
            radial-gradient(circle at 12% 8%, rgba(59,130,246,.20), transparent 40%),
            radial-gradient(circle at 88% 92%, rgba(168,85,247,.20), transparent 45%),
            linear-gradient(rgba(34,211,238,.04) 1px, transparent 1px) 0 0 / 42px 42px,
            linear-gradient(90deg, rgba(34,211,238,.04) 1px, transparent 1px) 0 0 / 42px 42px,
            #050816 !important;
        color:var(--text);
    }
    .stApp p, .stApp li, .stApp span, .stApp label{ color:var(--text); }
    /* Ocultar elementos genéricos de Streamlit */
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="InputInstructions"]{ display:none !important; }
    [data-testid="stHeader"]{ background:transparent !important; }
    .block-container{ max-width:880px; padding-top:1.6rem; padding-bottom:2rem;
                      position:relative; z-index:1; }

    /* ---------- Lluvia de 0 y 1 en el fondo ---------- */
    .fondo-binario{ position:fixed; inset:0; overflow:hidden; pointer-events:none; z-index:0; }
    .bit-col{ position:absolute; top:-110vh; font-family:var(--mono); font-size:15px;
              line-height:1.45; color:rgba(34,211,238,.12); animation:caer linear infinite; }
    .bit-col.morado{ color:rgba(168,85,247,.12); }
    .simbolo-fondo{ position:fixed; font-family:var(--mono); font-size:5rem; font-weight:800;
                    color:rgba(59,130,246,.06); pointer-events:none; z-index:0; }

    /* ---------- Barra superior del sistema ---------- */
    .topbar{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;
             gap:.5rem; font-family:var(--mono); font-size:.82rem; color:var(--muted);
             border:1px solid rgba(34,211,238,.18); background:rgba(5,10,30,.7);
             border-radius:12px; padding:.55rem 1rem; margin-bottom:1rem; }
    .topbar b{ color:var(--cyan); letter-spacing:.15em; }
    .estado-linea{ display:flex; align-items:center; gap:.45rem; color:#86efac; }
    .punto{ width:9px; height:9px; border-radius:50%; background:var(--green);
            box-shadow:0 0 10px var(--green); animation:parpadeo 1.6s infinite; }
    .capas{ display:flex; gap:.6rem; margin:0 0 1.2rem 0; }
    .capa{ flex:1; padding:.5rem .3rem; text-align:center; border-radius:10px;
           border:1px solid #1e293b; font-family:var(--mono); font-size:.78rem;
           color:#64748b; background:rgba(5,10,30,.6); }
    .capa.ok{ border-color:rgba(34,197,94,.6); color:#4ade80; }
    .capa.activa{ border-color:var(--cyan); color:var(--cyan); box-shadow:0 0 14px rgba(34,211,238,.3); }

    /* ---------- Tarjetas ---------- */
    .card{ background:var(--panel); border:1px solid rgba(34,211,238,.25); border-radius:20px;
           padding:2rem 2rem 1.6rem; margin-bottom:1.2rem; backdrop-filter:blur(6px);
           box-shadow:0 0 40px rgba(34,211,238,.08), inset 0 0 40px rgba(59,130,246,.05);
           animation:aparecer .6s ease-out; position:relative; }
    .card::before{ content:"</>"; position:absolute; top:.9rem; right:1.2rem;
                   font-family:var(--mono); color:rgba(168,85,247,.45); font-size:.9rem; }
    .etiqueta{ font-family:var(--mono); color:var(--cyan); letter-spacing:.45em;
               text-align:center; font-size:1.05rem; margin-bottom:.2rem; }
    .titulo{ text-align:center; font-size:3.1rem; font-weight:800; line-height:1.1;
             letter-spacing:.04em; margin:.2rem 0 .8rem;
             background:linear-gradient(90deg,var(--cyan),var(--blue),var(--purple));
             -webkit-background-clip:text; background-clip:text; color:transparent !important; }
    .mensaje{ text-align:center; font-size:1.18rem; line-height:1.7; color:var(--text);
              max-width:640px; margin:0 auto 1rem; }
    .icono{ font-size:4.2rem; text-align:center; line-height:1.2; }
    .chips{ display:flex; gap:.5rem; justify-content:center; flex-wrap:wrap; margin:.6rem 0 1rem; }
    .chip{ font-family:var(--mono); font-size:.8rem; padding:.25rem .75rem; border-radius:999px;
           border:1px solid rgba(168,85,247,.45); color:#c4b5fd !important;
           background:rgba(168,85,247,.08); }
    .red-neuronal{ display:block; margin:.4rem auto .8rem; width:260px; max-width:80%; }
    .sinapsis{ stroke:rgba(34,211,238,.35); stroke-width:1.2; stroke-dasharray:4 4;
               animation:flujo 1.4s linear infinite; }
    .neurona{ fill:#0b1430; stroke:var(--cyan); stroke-width:2; }
    .neurona.salida{ stroke:var(--purple); animation:pulso-svg 1.6s infinite; }

    /* ---------- Terminal ---------- */
    .terminal{ background:#020617; border:1px solid rgba(34,197,94,.35); border-radius:12px;
               padding:1rem 1.2rem; font-family:var(--mono); font-size:.95rem; line-height:1.75;
               margin:.6rem 0 1rem; }
    .terminal .t-linea{ color:#4ade80; }
    .terminal.rojo{ border-color:rgba(239,68,68,.45); }
    .terminal.rojo .t-linea{ color:#fca5a5; }
    .cursor::after{ content:"█"; animation:parpadeo 1s steps(1) infinite; }
    .barra{ height:10px; background:#0f172a; border-radius:99px; overflow:hidden; margin-top:.7rem;
            border:1px solid rgba(34,211,238,.25); }
    .barra-relleno{ height:100%; background:linear-gradient(90deg,var(--cyan),var(--purple));
                    box-shadow:0 0 12px var(--cyan); transition:width .4s; }
    .pct{ color:var(--muted) !important; font-size:.78rem; text-align:right; margin-top:.3rem; }

    /* ---------- Formularios y campos ---------- */
    [data-testid="stForm"]{ border:1px solid rgba(59,130,246,.3) !important; border-radius:16px !important;
                            background:rgba(5,10,30,.55); padding:1.2rem 1.2rem .6rem !important; }
    .stTextInput label p{ color:var(--muted) !important; font-family:var(--mono);
                          letter-spacing:.12em; font-size:.9rem !important; }
    .stTextInput div[data-baseweb="input"]{ background:#0a1128 !important; border-radius:12px !important;
                                            border:1px solid rgba(34,211,238,.45) !important; }
    .stTextInput div[data-baseweb="input"] > div{ background:transparent !important; }
    .stTextInput div[data-baseweb="input"]:focus-within{
        box-shadow:0 0 0 2px rgba(34,211,238,.35), 0 0 26px rgba(34,211,238,.25) !important; }
    .stTextInput input{ background:transparent !important; color:#e0f2fe !important;
                        -webkit-text-fill-color:#e0f2fe !important; caret-color:var(--cyan);
                        font-family:var(--mono) !important; font-size:2.1rem !important;
                        letter-spacing:.55em; text-align:center; padding:.7rem !important; }
    .stTextInput input::placeholder{ color:#334155 !important; -webkit-text-fill-color:#334155 !important; }

    /* ---------- Botones ---------- */
    .stButton > button, [data-testid="stFormSubmitButton"] > button{
        width:100%; min-height:3.5rem; border-radius:12px; font-family:var(--mono);
        transition:all .2s ease; }
    .stButton > button p, [data-testid="stFormSubmitButton"] > button p{
        font-size:1.12rem !important; font-weight:700 !important; letter-spacing:.12em;
        font-family:var(--mono); color:inherit !important; }
    button[kind="primary"], button[kind="primaryFormSubmit"],
    button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]{
        background:linear-gradient(90deg,#2563eb,#7c3aed) !important; color:#fff !important;
        border:1px solid rgba(34,211,238,.55) !important; box-shadow:0 0 18px rgba(59,130,246,.35); }
    button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover,
    button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover{
        transform:translateY(-2px); box-shadow:0 0 30px rgba(34,211,238,.55);
        border-color:var(--cyan) !important; }
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"]{
        background:rgba(5,10,30,.7) !important; color:var(--cyan) !important;
        border:1px solid rgba(34,211,238,.35) !important; }
    button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover{
        border-color:var(--cyan) !important; box-shadow:0 0 18px rgba(34,211,238,.3); }

    /* ---------- Avisos ---------- */
    .aviso{ border:1px solid rgba(250,204,21,.55); background:rgba(66,52,4,.55); color:#fde68a;
            border-radius:12px; padding:.8rem 1rem; font-family:var(--mono); margin:.6rem 0;
            animation:sacudir .4s; }
    .contador{ text-align:center; font-family:var(--mono); color:var(--muted); font-size:.85rem; }

    /* ---------- Pantallas de error ---------- */
    .card.error{ border-color:rgba(239,68,68,.65); background:rgba(40,8,18,.88);
                 box-shadow:0 0 50px rgba(239,68,68,.28), inset 0 0 40px rgba(239,68,68,.08);
                 animation:sacudir .55s; }
    .card.error::before{ color:rgba(239,68,68,.5); }
    .titulo-error{ text-align:center; font-family:var(--mono); font-size:2.7rem; font-weight:800;
                   color:#f87171 !important; letter-spacing:.08em; text-shadow:0 0 20px rgba(239,68,68,.6);
                   animation:alerta 1s infinite alternate; }

    /* ---------- Código correcto / desafío ---------- */
    .card.ok{ border-color:rgba(34,197,94,.55); box-shadow:0 0 45px rgba(34,197,94,.18); }
    .titulo-ok{ text-align:center; font-family:var(--mono); font-size:2.5rem; font-weight:800;
                color:#4ade80 !important; letter-spacing:.08em; text-shadow:0 0 18px rgba(34,197,94,.5); }
    .subtitulo{ text-align:center; font-size:1.25rem; color:var(--text); margin-bottom:.6rem; }
    .banner-desafio{ text-align:center; font-family:var(--mono); font-size:1.5rem; font-weight:800;
                     letter-spacing:.3em; color:#f0abfc !important; padding:.8rem; border-radius:12px;
                     border:1px dashed rgba(168,85,247,.6); background:rgba(168,85,247,.08);
                     animation:pulso 1.8s infinite; }
    .ayuda{ border-left:4px solid var(--cyan); background:rgba(34,211,238,.06); border-radius:10px;
            padding:.9rem 1.2rem; margin:.4rem 0 1rem; font-size:1.05rem; line-height:1.8; }
    .ayuda b{ color:var(--cyan); }
    .reglas{ display:flex; gap:.6rem; flex-wrap:wrap; margin-bottom:1rem; }
    .regla{ flex:1; min-width:170px; border:1px solid rgba(59,130,246,.3); border-radius:10px;
            padding:.55rem .7rem; font-size:.9rem; background:rgba(5,10,30,.6); }
    .regla b{ font-family:var(--mono); color:var(--purple); }
    .expresion{ font-family:var(--mono); font-size:1.75rem; text-align:center; padding:1.4rem 1rem;
                background:#020617; border-radius:14px; border:1px solid rgba(168,85,247,.5);
                box-shadow:inset 0 0 30px rgba(168,85,247,.12); margin:.4rem 0 1.2rem;
                word-break:break-word; line-height:1.6; }
    .expresion .op{ color:#c084fc !important; font-weight:800; }
    .expresion .bit{ color:var(--cyan) !important; font-weight:800; }
    .expresion .p1{ color:#64748b !important; } .expresion .p2{ color:#60a5fa !important; }
    .expresion .p3{ color:#f472b6 !important; } .expresion .igual{ color:#fde047 !important; font-weight:800; }

    /* ---------- Pantalla final ---------- */
    .card.exito{ border-color:rgba(34,197,94,.75); background:rgba(4,30,20,.9);
                 box-shadow:0 0 70px rgba(34,197,94,.35), inset 0 0 50px rgba(34,197,94,.1);
                 animation:aparecer .8s ease-out; }
    .card.exito::before{ color:rgba(34,197,94,.6); }
    .candado{ font-size:5.5rem; text-align:center; animation:abrir 1.2s ease-out; }
    .boveda{ width:120px; height:120px; margin:0 auto .6rem; border-radius:50%;
             border:6px double rgba(34,197,94,.75); display:flex; align-items:center;
             justify-content:center; box-shadow:0 0 35px rgba(34,197,94,.5);
             animation:girar 2.2s ease-out; }
    .titulo-exito{ text-align:center; font-family:var(--mono); font-size:2.9rem; font-weight:800;
                   color:#4ade80 !important; letter-spacing:.08em; animation:brillo 1.6s infinite alternate; }
    .subtitulo-exito{ text-align:center; font-size:1.9rem; font-weight:800; color:#bbf7d0 !important;
                      letter-spacing:.12em; }
    .felicitacion{ text-align:center; font-size:1.5rem; margin:.4rem 0 .8rem; color:#fef08a !important; }

    .pie{ text-align:center; font-family:var(--mono); color:#475569 !important; font-size:.8rem;
          margin-top:1.6rem; letter-spacing:.1em; }

    /* ---------- Animaciones ---------- */
    @keyframes caer{ from{ transform:translateY(0); } to{ transform:translateY(230vh); } }
    @keyframes parpadeo{ 0%,100%{ opacity:1; } 50%{ opacity:.25; } }
    @keyframes aparecer{ from{ opacity:0; transform:translateY(14px); } to{ opacity:1; transform:none; } }
    @keyframes sacudir{ 0%,100%{ transform:translateX(0); } 20%{ transform:translateX(-10px); }
                        40%{ transform:translateX(10px); } 60%{ transform:translateX(-6px); }
                        80%{ transform:translateX(6px); } }
    @keyframes alerta{ from{ opacity:1; } to{ opacity:.6; } }
    @keyframes pulso{ 0%,100%{ box-shadow:0 0 0 rgba(168,85,247,0); }
                      50%{ box-shadow:0 0 24px rgba(168,85,247,.45); } }
    @keyframes pulso-svg{ 0%,100%{ fill:#0b1430; } 50%{ fill:#a855f7; } }
    @keyframes flujo{ to{ stroke-dashoffset:-16; } }
    @keyframes brillo{ from{ text-shadow:0 0 10px rgba(34,197,94,.5); }
                       to{ text-shadow:0 0 35px rgba(34,197,94,1); } }
    @keyframes abrir{ 0%{ transform:scale(.3) rotate(-25deg); opacity:0; }
                      60%{ transform:scale(1.2) rotate(8deg); opacity:1; }
                      100%{ transform:scale(1) rotate(0); } }
    @keyframes girar{ from{ transform:rotate(-360deg) scale(.5); } to{ transform:rotate(0) scale(1); } }

    /* ---------- Pantallas pequeñas ---------- */
    @media (max-width:640px){
        .titulo{ font-size:2.1rem; } .titulo-error, .titulo-exito{ font-size:1.9rem; }
        .titulo-ok{ font-size:1.8rem; } .expresion{ font-size:1.15rem; }
        .stTextInput input{ font-size:1.5rem !important; letter-spacing:.3em; }
        .card{ padding:1.4rem 1.1rem 1.2rem; }
    }
    </style>
    """)


def fondo_decorativo() -> None:
    """Columnas de 0 y 1 cayendo + símbolos de datos/IA (semilla fija = sin parpadeos)."""
    rng = random.Random(2026)
    columnas = []
    for i in range(24):
        bits = "<br>".join(rng.choice("01") for _ in range(34))
        izquierda = i * 4.2 + rng.uniform(0, 2)
        duracion = rng.uniform(16, 30)
        retraso = -rng.uniform(0, 25)
        clase = "bit-col morado" if i % 3 == 0 else "bit-col"
        columnas.append(
            f'<div class="{clase}" style="left:{izquierda:.1f}%;'
            f'animation-duration:{duracion:.1f}s;animation-delay:{retraso:.1f}s">{bits}</div>'
        )
    simbolos = (
        '<div class="simbolo-fondo" style="top:12%;left:3%">&lt;/&gt;</div>'
        '<div class="simbolo-fondo" style="bottom:8%;right:4%">{ }</div>'
        '<div class="simbolo-fondo" style="top:55%;left:2%;font-size:3.5rem">🗄</div>'
    )
    html(f'<div class="fondo-binario">{"".join(columnas)}{simbolos}</div>')


def barra_superior() -> None:
    """Cabecera tipo sistema de seguridad + indicador de capas superadas."""
    ss = st.session_state
    etapa = ss.etapa

    def clase(n: int) -> str:
        if n == 1:
            return "ok" if ss.codigo_validado else "activa"
        if n == 2:
            if ss.final_validado:
                return "ok"
            return "activa" if ss.codigo_validado else ""
        return "ok" if etapa == "exito" else ""

    html(f"""
    <div class="topbar">
        <span><b>SISTEMA DE SEGURIDAD</b> · NODO CENTRAL DE DATOS</span>
        <span class="estado-linea"><span class="punto"></span>EN LÍNEA</span>
    </div>
    <div class="capas">
        <div class="capa {clase(1)}">CAPA 1 · SECUENCIA BINARIA</div>
        <div class="capa {clase(2)}">CAPA 2 · COMPUERTA FINAL</div>
        <div class="capa {clase(3)}">🔐 BÓVEDA</div>
    </div>
    """)


def pie() -> None:
    html('<div class="pie">ESTACIÓN 1 · INGENIERÍA DE DATOS E INTELIGENCIA ARTIFICIAL · AND · OR · NOT</div>')


# =====================================================================
# 5. PANTALLAS
# =====================================================================
def pantalla_inicio() -> None:
    """PANTALLA 1: bienvenida + ingreso del código de 8 dígitos."""
    html(f"""
    <div class="card">
        <div class="icono">🔐</div>
        <div class="etiqueta">ESTACIÓN 1</div>
        <div class="titulo">DESBLOQUEA EL CÓDIGO</div>
        {svg_red_neuronal()}
        <div class="mensaje">
            Han llegado al <b>sistema central</b>. Si resolvieron correctamente los
            <b>8 sobres</b>, ya tienen en sus manos el código de acceso.
            Ingrésenlo para continuar.
        </div>
        <div class="chips">
            <span class="chip">AND</span><span class="chip">OR</span><span class="chip">NOT</span>
            <span class="chip">&lt;/&gt; CÓDIGO</span><span class="chip">🗄 DATOS</span>
            <span class="chip">🧠 IA</span>
        </div>
        {terminal(["&gt; Sistema de seguridad activo.",
                   "&gt; Esperando secuencia de acceso de 8 dígitos..."], cursor=True)}
    </div>
    """)

    with st.form("form_codigo", clear_on_submit=False):
        codigo = st.text_input(
            "CÓDIGO DE ACCESO · 8 DÍGITOS",
            max_chars=8,
            placeholder="········",
            key="input_codigo",
            autocomplete="off",   # evita que el navegador sugiera el código al siguiente equipo
        )
        enviado = st.form_submit_button("VALIDAR CÓDIGO", type="primary")

    if st.session_state.intentos_codigo > 0:
        html(f'<div class="contador">Intentos fallidos registrados: {st.session_state.intentos_codigo}</div>')

    if enviado:
        codigo = (codigo or "").strip()  # se maneja SIEMPRE como texto

        # --- Validación de la entrada (no cuenta como intento) ---
        if not codigo:
            aviso("Debes ingresar el código antes de validar.")
            return
        if not codigo.isdigit():
            aviso("El código solo puede contener números.")
            return
        if len(codigo) != 8:
            aviso(f"El código debe tener exactamente 8 dígitos (ingresaste {len(codigo)}).")
            return

        # --- Validación del código ---
        animacion_validacion([
            "Analizando código...",
            "Validando secuencia binaria...",
            "Comparando con la llave del sistema...",
        ])
        if coincide(codigo, HASH_CODIGO):
            st.session_state.codigo_validado = True
            st.session_state.etapa = "codigo_ok"
        else:
            st.session_state.codigo_validado = False
            st.session_state.intentos_codigo += 1
            st.session_state.etapa = "error_codigo"
        st.rerun()


def pantalla_error_codigo() -> None:
    """Código incorrecto: no permite avanzar."""
    html(f"""
    <div class="card error">
        <div class="icono">❌</div>
        <div class="titulo-error">ACCESO DENEGADO</div>
        <div class="mensaje">
            El código ingresado no coincide. Revisen los resultados de los
            <b>8 sobres</b> e inténtenlo nuevamente.
        </div>
        {terminal(["&gt; Validando secuencia binaria... FALLO",
                   "&gt; Acceso denegado. La capa 1 permanece bloqueada.",
                   f"&gt; Intentos fallidos: {st.session_state.intentos_codigo}"], clase="rojo")}
    </div>
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.button("← VOLVER", on_click=volver_a_inicio, key="volver_err_cod")
    with col2:
        st.button("🔁 INTENTAR DE NUEVO", on_click=volver_a_inicio, type="primary", key="reint_cod")


def pantalla_codigo_ok() -> None:
    """Código correcto: primera barrera superada, pero la bóveda sigue cerrada."""
    html(f"""
    <div class="card ok">
        <div class="icono">✅</div>
        <div class="titulo-ok">CÓDIGO CORRECTO</div>
        <div class="subtitulo">Primera barrera superada.</div>
        {terminal(["&gt; Capa 1 · Secuencia binaria ........ [ OK ]",
                   "&gt; Detectando capas restantes...",
                   "&gt; ALERTA: la bóveda tiene una última capa de seguridad."])}
        <div class="banner-desafio">⚡ DESAFÍO FINAL ⚡</div>
    </div>
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.button("← VOLVER", on_click=volver_a_inicio, key="volver_ok")
    with col2:
        st.button("IR AL DESAFÍO FINAL →", on_click=ir_a, args=("desafio",), type="primary", key="ir_desafio")


def pantalla_desafio() -> None:
    """PANTALLA 2: último ejercicio con AND, OR y NOT."""
    expresion = (
        '<span class="op">NOT</span> <span class="p1">(</span><span class="p2">(</span>'
        '<span class="bit">1</span> <span class="op">AND</span> <span class="bit">0</span>'
        '<span class="p2">)</span> <span class="op">OR</span> <span class="p2">(</span>'
        '<span class="p3">(</span><span class="op">NOT</span> <span class="bit">0</span>'
        '<span class="p3">)</span> <span class="op">AND</span> <span class="bit">1</span>'
        '<span class="p2">)</span><span class="p1">)</span> <span class="igual">= ?</span>'
    )
    html(f"""
    <div class="card">
        <div class="icono">🧠</div>
        <div class="etiqueta">ÚLTIMA CAPA DE SEGURIDAD</div>
        <div class="titulo">DESAFÍO FINAL</div>
        <div class="ayuda">
            <b>Recuerda:</b><br>
            1. Resuelve primero los paréntesis internos.<br>
            2. Aplica <b>NOT</b> cuando corresponda.<br>
            3. Continúa de adentro hacia afuera.
        </div>
        <div class="reglas">
            <div class="regla"><b>AND</b> → 1 solo si ambas entradas son 1</div>
            <div class="regla"><b>OR</b> → 1 si al menos una entrada es 1</div>
            <div class="regla"><b>NOT</b> → invierte el valor</div>
        </div>
        <div class="expresion">{expresion}</div>
        <div class="mensaje">Desarróllenlo paso a paso en papel y escriban
        <b>solo el resultado final</b>.</div>
    </div>
    """)

    with st.form("form_final", clear_on_submit=False):
        respuesta = st.text_input(
            "RESULTADO FINAL · ESCRIBE 0 O 1",
            max_chars=1,
            placeholder="?",
            key="input_final",
            autocomplete="off",
        )
        enviado = st.form_submit_button("VALIDAR RESPUESTA FINAL", type="primary")

    if st.session_state.intentos_final > 0:
        html(f'<div class="contador">Intentos fallidos en esta capa: {st.session_state.intentos_final}</div>')

    if enviado:
        respuesta = (respuesta or "").strip()
        if not respuesta:
            aviso("Debes escribir una respuesta antes de validar.")
        elif respuesta not in ("0", "1"):
            aviso("Respuesta no válida: solo se acepta un 0 o un 1.")
        else:
            animacion_validacion([
                "Evaluando compuertas lógicas...",
                "Propagando señal por el circuito...",
                "Verificando última capa de seguridad...",
            ])
            if coincide(respuesta, HASH_RESPUESTA_FINAL):
                st.session_state.final_validado = True
                st.session_state.celebrado = False
                st.session_state.etapa = "exito"
            else:
                st.session_state.final_validado = False
                st.session_state.intentos_final += 1
                st.session_state.etapa = "error_final"
            st.rerun()

    st.button("← VOLVER", on_click=ir_a, args=("codigo_ok",), key="volver_desafio")


def pantalla_error_final() -> None:
    """Respuesta final incorrecta: no revela la solución."""
    html(f"""
    <div class="card error">
        <div class="icono">🔒</div>
        <div class="titulo-error">RESPUESTA INCORRECTA</div>
        <div class="mensaje">La bóveda permanece bloqueada.</div>
        {terminal(["&gt; Evaluando compuertas lógicas... FALLO",
                   "&gt; Capa 2 · Compuerta final ........ [ BLOQUEADA ]",
                   f"&gt; Intentos fallidos: {st.session_state.intentos_final}"], clase="rojo")}
    </div>
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.button("← VOLVER", on_click=ir_a, args=("desafio",), key="volver_err_fin")
    with col2:
        st.button("🔁 INTENTAR DE NUEVO", on_click=ir_a, args=("desafio",), type="primary", key="reint_fin")


def pantalla_exito() -> None:
    """Pantalla final: bóveda desbloqueada."""
    if not st.session_state.celebrado:
        st.balloons()
        st.session_state.celebrado = True

    html(f"""
    <div class="card exito">
        <div class="boveda"><div class="candado">🔓</div></div>
        <div class="titulo-exito">ACCESO CONCEDIDO</div>
        <div class="subtitulo-exito">BÓVEDA DESBLOQUEADA</div>
        <div class="felicitacion">🏆 ¡Estación superada! 🏆</div>
        {terminal(["&gt; Capa 1 · Secuencia binaria ........ [ OK ]",
                   "&gt; Capa 2 · Compuerta final .......... [ OK ]",
                   "&gt; Desencriptando bóveda ............. 100%",
                   "&gt; SISTEMA DESBLOQUEADO. Bienvenidos, ingenieros."], cursor=True)}
    </div>
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.button("← VOLVER", on_click=volver_al_desafio, key="volver_exito")
    with col2:
        st.button("⟳ REINICIAR ESTACIÓN", on_click=reiniciar_estacion, type="primary", key="reiniciar")


# =====================================================================
# 6. ENRUTADOR PRINCIPAL
# =====================================================================
PANTALLAS = {
    "inicio": pantalla_inicio,
    "error_codigo": pantalla_error_codigo,
    "codigo_ok": pantalla_codigo_ok,
    "desafio": pantalla_desafio,
    "error_final": pantalla_error_final,
    "exito": pantalla_exito,
}


def main() -> None:
    inicializar_estado()
    ss = st.session_state

    # Protecciones: nadie llega a una etapa sin haber superado la anterior.
    if ss.etapa not in PANTALLAS:
        ss.etapa = "inicio"
    if ss.etapa in ("codigo_ok", "desafio", "error_final") and not ss.codigo_validado:
        ss.etapa = "inicio"
    if ss.etapa == "exito" and not (ss.codigo_validado and ss.final_validado):
        ss.etapa = "inicio"

    inyectar_css()
    fondo_decorativo()
    barra_superior()
    PANTALLAS[ss.etapa]()
    pie()


main()