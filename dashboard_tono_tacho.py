
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

df = pd.read_csv("data.csv")

# Normalize percentages
for col in ["% Aprobado", "% Consecionado", "% Rechazado"]:
    if df[col].max() <= 1:
        df[col] *= 100

# Filters
st.sidebar.markdown("### 🗂️ Filtros")
semanas = df["Semana"].dropna().unique().tolist()
opciones_semanas = ["Todas"] + semanas
semana_seleccionada = st.sidebar.multiselect("Selecciona semana(s):", opciones_semanas, default=["Todas"])
if "Todas" in semana_seleccionada:
    semana_seleccionada = semanas

tipos_partida = ["Aprobado", "Consecionado", "Rechazado"]
tipo_partida = st.sidebar.multiselect("Selecciona tipo(s):", tipos_partida, default=tipos_partida)

# Filter dataframe
df_filtrado = df[df["Semana"].isin(semana_seleccionada)]

# Title and KPIs
st.title("Dashboard de Evaluación del Tono en Tacho")
st.markdown("### 📊 Indicadores clave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total evaluadas", int(df_filtrado["Total partidas evaluadas"].sum()))
col2.metric("% Aprobado promedio", f'{df_filtrado["% Aprobado"].mean():.2f}%')
col3.metric("% Consecionado promedio", f'{df_filtrado["% Consecionado"].mean():.2f}%')
col4.metric("% Rechazado promedio", f'{df_filtrado["% Rechazado"].mean():.2f}%')

# Bar chart
st.markdown("---")
st.header("📦 Distribución de partidas por semana")
df_bar = df_filtrado[["Semana"] + tipo_partida]
df_bar_plot = pd.melt(df_bar, id_vars=["Semana"], value_vars=tipo_partida,
                      var_name="Tipo", value_name="Cantidad")
color_map = {"Aprobado": "green", "Consecionado": "gold", "Rechazado": "red"}
fig_bar = px.bar(df_bar_plot, x="Semana", y="Cantidad", color="Tipo", barmode="stack",
                 color_discrete_map=color_map)

# Annotations: totals for selected types
totales = df_filtrado.groupby("Semana")[tipo_partida].sum().reset_index()
for _, row in totales.iterrows():
    total_val = row[tipo_partida].sum() if isinstance(row[tipo_partida], pd.Series) else sum(row[tipo_partida])
    fig_bar.add_annotation(x=row["Semana"], y=total_val,
                           text=f'{int(total_val)}',
                           showarrow=False, font=dict(size=14, color="black"),
                           xanchor="center", yanchor="bottom")
fig_bar.update_layout(yaxis_title="Cantidad de partidas", title_text="")
st.plotly_chart(fig_bar, use_container_width=True)

# Line chart
st.markdown("---")
st.header("📉 Tendencia del % Rechazado")
fig_line = px.line(df_filtrado, x="Semana", y="% Rechazado", markers=True)
fig_line.update_traces(line=dict(color="red"), marker=dict(size=8), text=df_filtrado["% Rechazado"].round(1))
fig_line.update_traces(mode="lines+markers+text", textposition="top center")
fig_line.update_layout(yaxis_title="% Rechazado", xaxis_title="Semana",
                       yaxis_range=[0, max(df_filtrado["% Rechazado"].max()+5,20)], title_text="")
st.plotly_chart(fig_line, use_container_width=True)

# Donut chart with fixed colors
st.markdown("---")
st.header("🧭 Distribución general de partidas")
totales_donut = df_filtrado[["Aprobado", "Consecionado", "Rechazado"]].sum()
labels = totales_donut.index.tolist()
values = totales_donut.values.tolist()
colors = [color_map[label] for label in labels]
fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
fig_donut.update_layout(title_text="")
st.plotly_chart(fig_donut, use_container_width=True)
