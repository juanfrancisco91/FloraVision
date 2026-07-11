import streamlit as st
import pandas as pd
import random

# ==========================
# CONFIGURACIÓN GENERAL
# ==========================

st.set_page_config(
    page_title="FloraVision",
    page_icon="🌸",
    layout="wide"
)

# ==========================
# ESTILOS PERSONALIZADOS
# ==========================

st.markdown("""
<style>

.main{
background-color:#f8f4f5;
}

section[data-testid="stSidebar"]{
background-color:#6d003c;
color:white;
}

.stButton>button{
background-color:#b78a00;
color:white;
border-radius:10px;
width:100%;
}

.metric-box{
padding:15px;
border-radius:10px;
background:white;
box-shadow:0px 0px 8px rgba(0,0,0,.1);
}

</style>
""",unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("🌸 FloraVision")

pagina=st.sidebar.radio(

"Menú",

[
"Dashboard",
"Detección",
"Inventario",
"Reportes",
"Configuración"
]

)

st.sidebar.write("---")

st.sidebar.success("🟢 IA Activa")
st.sidebar.info("📷 Cámara conectada")

# ==========================
# DATOS SIMULADOS
# ==========================

flores=["Rosa","Lirio","Tulipán","Orquídea"]

flor=random.choice(flores)

estado=random.choice(
[
"Saludable",
"Deterioro leve",
"Deterioro severo"
]
)

precio=200

if estado=="Saludable":

    descuento=0
    nuevo=200
    color="🟢"

elif estado=="Deterioro leve":

    descuento=15
    nuevo=170
    color="🟡"

else:

    descuento=40
    nuevo=120
    color="🔴"

# ==========================
# DASHBOARD
# ==========================

if pagina=="Dashboard":

    st.title("🌸 Dashboard FloraVision")

    c1,c2,c3,c4=st.columns(4)

    c1.metric(
        "Inventario Total",
        "850"
    )

    c2.metric(
        "🟢 Saludables",
        "720"
    )

    c3.metric(
        "🟡 Riesgo",
        "100"
    )

    c4.metric(
        "🔴 Críticas",
        "30"
    )

    st.write("---")

    g1,g2=st.columns([2,1])

    with g1:

        st.subheader(
        "📈 Estado semanal"
        )

        datos=pd.DataFrame({

        "Saludables":[30,50,60,70],
        "Riesgo":[20,15,10,8],
        "Críticas":[8,7,5,2]

        })

        st.line_chart(datos)

    with g2:

        st.subheader(
        "💰 Pérdidas evitadas"
        )

        st.metric(
        "RD$",
        "12,500",
        "+18%"
        )

# ==========================
# DETECCIÓN
# ==========================

elif pagina=="Detección":

    st.title(
    "📷 Detección Inteligente"
    )

    izquierda,derecha=st.columns(
    [2,1]
    )

    with izquierda:

        imagen=st.camera_input(
        "Capturar flor"
        )

        b1,b2,b3=st.columns(3)

        with b1:
            st.button(
            "▶ Iniciar"
            )

        with b2:
            st.button(
            "⏸ Pausar"
            )

        with b3:
            st.button(
            "📸 Analizar"
            )

    with derecha:

        st.subheader(
        "🧠 Resultado"
        )

        st.write(
        f"Flor: {flor}"
        )

        st.write(
        f"Estado: {color} {estado}"
        )

        st.write(
        f"Precio original: RD${precio}"
        )

        st.write(
        f"Nuevo precio: RD${nuevo}"
        )

        st.write(
        f"Descuento: {descuento}%"
        )

        if estado=="Deterioro leve":

            st.warning(
            "Aplicar descuento recomendado"
            )

        elif estado=="Deterioro severo":

            st.error(
            "Producto próximo a pérdida"
            )

        else:

            st.success(
            "Producto saludable"
            )

# ==========================
# INVENTARIO
# ==========================

elif pagina=="Inventario":

    st.title(
    "🌸 Inventario"
    )

    tabla=pd.DataFrame({

    "Flor":[
    "Rosa",
    "Tulipán",
    "Lirio",
    "Orquídea"
    ],

    "Estado":[
    "🟢",
    "🟡",
    "🔴",
    "🟢"
    ],

    "Precio":[
    "RD$200",
    "RD$150",
    "RD$90",
    "RD$300"
    ],

    "Acción":[
    "Mantener",
    "Aplicar -15%",
    "Retirar",
    "Mantener"
    ]

    })

    st.dataframe(
    tabla,
    use_container_width=True
    )

# ==========================
# REPORTES
# ==========================

elif pagina=="Reportes":

    st.title(
    "📊 Reportes"
    )

    datos=pd.DataFrame({

    "Categoría":[
    "Saludables",
    "Riesgo",
    "Críticas"
    ],

    "Cantidad":[
    720,
    100,
    30
    ]

    })

    st.bar_chart(
    datos.set_index(
    "Categoría"
    )
    )

# ==========================
# CONFIGURACIÓN
# ==========================

elif pagina=="Configuración":

    st.title(
    "⚙ Configuración"
    )

    sensibilidad=st.slider(

    "Sensibilidad IA",

    0,
    100,
    80

    )

    descuento_auto=st.checkbox(
    "Activar descuentos automáticos"
    )

    modelo=st.selectbox(

    "Modelo IA",

    [
    "MobileNet",
    "ResNet"
    ]

    )

    st.write("---")

    st.success(
    "Configuración guardada"
    )