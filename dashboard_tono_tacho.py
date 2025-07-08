
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Cargar datos
df = pd.read_csv("data.csv")

# Normalizar porcentajes solo si la columna existe
for col in ["% Aprobado", "% Concesionado", "% Rechazado"]:
    if col in df.columns:
        if df[col].max() <= 1:
            df[col] = df[col] * 100

# Filtros
st.sidebar.markdown("### 🗂️ Filtros")
semanas = sorted(df["Semana"].dropna().unique().tolist())
opciones_semanas = ["Todas"] + semanas
semana_seleccionada = st.sidebar.multiselect(
    "Selecciona semana(s):", opciones_semanas, default=["Todas"]
)
if "Todas" in semana_seleccionada:
    semana_seleccionada = semanas

tipos = ["Aprobado", "Consecionado", "Rechazado"]
opciones_tipos = ["Todos"] + tipos
tipo_seleccionado = st.sidebar.multiselect(
    "Selecciona tipo(s):", opciones_tipos, default=["Todos"]
)
if "Todos" in tipo_seleccionado:
    tipo_seleccionado = tipos

# Aplicar filtro por semana y tipo
df_filtrado = df[df["Semana"].isin(semana_seleccionada)]
# Mantener solo columnas seleccionadas
df_filtrado = df_filtrado[["Semana"] + tipo_seleccionado + ["Total partidas evaluadas"]]

# Título e indicadores
st.title("Dashboard de Evaluación del Tono en Tacho")
st.markdown("### 📊 Indicadores clave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total evaluadas", int(df_filtrado["Total partidas evaluadas"].sum()))
col2.metric("% Aprobado promedio", f'{df_filtrado["% Aprobado"].mean():.2f}%' if "% Aprobado" in df_filtrado.columns else "N/A")
col3.metric("% Concesionado promedio", f'{df_filtrado["% Concesionado"].mean():.2f}%' if "% Concesionado" in df_filtrado.columns else "N/A")
col4.metric("% Rechazado promedio", f'{df_filtrado["% Rechazado"].mean():.2f}%' if "% Rechazado" in df_filtrado.columns else "N/A")

# Gráfico de barras
st.markdown("---")
st.header("📦 Distribución de partidas por semana")
df_bar_plot = pd.melt(
    df_filtrado,
    id_vars=["Semana"],
    value_vars=tipo_seleccionado,
    var_name="Tipo",
    value_name="Cantidad"
)
color_map = {"Aprobado": "green", "Consecionado": "gold", "Rechazado": "red"}
fig_bar = px.bar(
    df_bar_plot,
    x="Semana",
    y="Cantidad",
    color="Tipo",
    barmode="stack",
    color_discrete_map=color_map
)
# Anotaciones de totales
totales = df_filtrado[tipo_seleccionado].sum(axis=1).tolist()
for idx, semana in enumerate(df_filtrado["Semana"]):
    fig_bar.add_annotation(
        x=semana,
        y=totales[idx],
        text=str(int(totales[idx])),
        showarrow=False,
        font=dict(size=14, color="black"),
        xanchor="center",
        yanchor="bottom"
    )
fig_bar.update_layout(yaxis_title="Cantidad de partidas", title_text="")
st.plotly_chart(fig_bar, use_container_width=True)

# Gráfico de línea del % Rechazado
st.markdown("---")
st.header("📉 Tendencia del % Rechazado")
fig_line = px.line(
    df_filtrado, x="Semana", y="% Rechazado" if "% Rechazado" in df_filtrado.columns else df_filtrado.columns[-1], markers=True
)
if "% Rechazado" in df_filtrado.columns:
    fig_line.update_traces(
        line=dict(color="red"),
        marker=dict(size=8),
        text=df_filtrado["% Rechazado"].round(1)
    )
    fig_line.update_traces(mode="lines+markers+text", textposition="top center")
    fig_line.update_layout(
        yaxis_title="% Rechazado",
        xaxis_title="Semana",
        title_text="",
        yaxis_range=[0, max(df_filtrado["% Rechazado"].max() + 5, 20)]
    )
st.plotly_chart(fig_line, use_container_width=True)

# Gráfico de donut estático
st.markdown("---")
st.header("🧭 Distribución general de partidas")
if all(col in df.columns for col in ["Aprobado", "Consecionado", "Rechazado"]):
    totales_donut = df[["Aprobado", "Consecionado", "Rechazado"]].sum()
    labels = totales_donut.index.tolist()
    values = totales_donut.values.tolist()
    colors = [color_map[label] for label in labels]
    fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
    fig_donut.update_layout(title_text="")
    st.plotly_chart(fig_donut, use_container_width=True)
