import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Wide layout
st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("data.csv")

# Normalize percentages if in 0-1
for col in ["% Aprobado", "% Concesionado", "% Rechazado"]:
    if df[col].max() <= 1:
        df[col] *= 100

# Sidebar filters
st.sidebar.markdown("### 🗂️ Filtros")

# Semana filter with 'Todas' option
semanas = sorted(df["Semana"].dropna().unique().tolist())
opciones_semanas = ["Todas"] + semanas
semana_seleccionada = st.sidebar.multiselect(
    "Selecciona semana(s):", opciones_semanas, default=["Todas"]
)
if "Todas" in semana_seleccionada:
    semana_seleccionada = semanas

# Tipo filter with 'Todos' option
tipos = ["Aprobado", "Concesionado", "Rechazado"]
opciones_tipos = ["Todos"] + tipos
tipo_seleccionado = st.sidebar.multiselect(
    "Selecciona tipo(s):", opciones_tipos, default=["Todos"]
)
if "Todos" in tipo_seleccionado:
    tipo_seleccionado = tipos

# Filter dataframe
df_filtrado = df[df["Semana"].isin(semana_seleccionada)]
df_filtrado = df_filtrado[["Semana"] + tipo_seleccionado + ["Total partidas evaluadas"]]

# Title
st.title("Dashboard de Evaluación del Tono en Tacho")
st.markdown("### 📊 Indicadores clave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total evaluadas", int(df_filtrado["Total partidas evaluadas"].sum()))
col2.metric("% Aprobado promedio", f'{df_filtrado["% Aprobado"].mean():.2f}%')
col3.metric("% Concesionado promedio", f'{df_filtrado["% Concesionado"].mean():.2f}%')
col4.metric("% Rechazado promedio", f'{df_filtrado["% Rechazado"].mean():.2f}%')

# Bar chart
st.markdown("---")
st.header("📦 Distribución de partidas por semana")
df_bar_plot = pd.melt(
    df_filtrado,
    id_vars=["Semana"],
    value_vars=tipo_seleccionado,
    var_name="Tipo",
    value_name="Cantidad"
)
color_map = {"Aprobado": "green", "Concesionado": "gold", "Rechazado": "red"}
fig_bar = px.bar(
    df_bar_plot,
    x="Semana",
    y="Cantidad",
    color="Tipo",
    barmode="stack",
    color_discrete_map=color_map
)
# Annotations: total of selected types
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

# Line chart
st.markdown("---")
st.header("📉 Tendencia del % Rechazado")
fig_line = px.line(
    df_filtrado, x="Semana", y="% Rechazado", markers=True
)
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

# Donut chart (fixed real %)
st.markdown("---")
st.header("🧭 Distribución general de partidas")
totales_donut = df_filtrado[["Aprobado", "Concesionado", "Rechazado"]].sum()
labels = totales_donut.index.tolist()
values = totales_donut.values.tolist()
colors = [color_map.get(label, "#BBBBBB") for label in labels]
fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
fig_donut.update_layout(title_text="")
st.plotly_chart(fig_donut, use_container_width=True)