
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

df = pd.read_csv("data.csv")

for col in ["% Aprobado", "% Consecionado", "% Rechazado"]:
    if df[col].max() <= 1:
        df[col] = df[col] * 100

st.sidebar.markdown("### 🗂️ Filtros")
semanas = df["Semana"].unique()
tipos_partida = ["Aprobado", "Consecionado", "Rechazado"]
semana_seleccionada = st.sidebar.multiselect("Selecciona semana(s):", semanas, default=semanas)
tipo_partida = st.sidebar.multiselect("Selecciona tipo(s):", tipos_partida, default=tipos_partida)
df_filtrado = df[df["Semana"].isin(semanas)]

st.title("Dashboard de Evaluación del Tono en Tacho")
st.markdown("### 📊 Indicadores clave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total evaluadas", int(df_filtrado["Total partidas evaluadas"].sum()))
col2.metric("% Aprobado promedio", f'{df_filtrado["% Aprobado"].mean():.2f}%')
col3.metric("% Consecionado promedio", f'{df_filtrado["% Consecionado"].mean():.2f}%')
col4.metric("% Rechazado promedio", f'{df_filtrado["% Rechazado"].mean():.2f}%')

st.markdown("---")
st.markdown("### 📦 Distribución de partidas por semana")
df_bar = df_filtrado[["Semana"] + tipo_partida + ["Total partidas evaluadas"]]
df_bar_plot = pd.melt(df_bar, id_vars=["Semana", "Total partidas evaluadas"], value_vars=tipo_partida,
                      var_name="Tipo", value_name="Cantidad")
color_map = {"Aprobado": "green", "Consecionado": "gold", "Rechazado": "red"}
fig_bar = px.bar(df_bar_plot, x="Semana", y="Cantidad", color="Tipo", barmode="stack",
                 color_discrete_map=color_map)
totales = df_bar.groupby("Semana")["Total partidas evaluadas"].first().reset_index()
for i, row in totales.iterrows():
    fig_bar.add_annotation(x=row["Semana"], y=row["Total partidas evaluadas"],
                           text=f'{int(row["Total partidas evaluadas"])}',
                           showarrow=False, font=dict(size=14, color="black"),
                           xanchor="center", yanchor="bottom")
fig_bar.update_layout(yaxis_title="Cantidad de partidas", title_text="")
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.markdown("### 📉 Tendencia del % Rechazado")
fig_line = px.line(df_filtrado, x="Semana", y="% Rechazado", markers=True)
fig_line.update_traces(line=dict(color="red"), marker=dict(size=8), text=df_filtrado["% Rechazado"].round(1))
fig_line.update_traces(mode="lines+markers+text", textposition="top center")
fig_line.update_layout(yaxis_title="% Rechazado", xaxis_title="Semana",
                       yaxis_range=[0, max(df_filtrado["% Rechazado"].max() + 5, 20)],
                       title_text="")
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")
st.markdown("### 🧭 Distribución general de partidas")
totales = df_filtrado[["Aprobado", "Consecionado", "Rechazado"]].sum()
fig_donut = go.Figure(data=[go.Pie(labels=totales.index, values=totales.values, hole=0.5,
                                   marker=dict(colors=["green", "gold", "red"]))])
fig_donut.update_layout(title_text="")
st.plotly_chart(fig_donut, use_container_width=True)
