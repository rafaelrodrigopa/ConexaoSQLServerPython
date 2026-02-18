import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título
st.title("📊 Painel Interativo - Exemplo Simples")

# Base de dados de exemplo
df = pd.DataFrame({
    "Categoria": ["A", "B", "C", "D"],
    "Valor": [10, 25, 15, 30]
})

# Sidebar (painel lateral)
st.sidebar.header("Filtros")

# Slider interativo
fator = st.sidebar.slider("Multiplicador:", 1, 5, 1)

# Aplicando filtro
df["Valor Ajustado"] = df["Valor"] * fator

# Mostrar tabela
st.subheader("Tabela de Dados")
st.dataframe(df)

# Criar gráfico
st.subheader("Gráfico de Barras")

fig, ax = plt.subplots()
ax.bar(df["Categoria"], df["Valor Ajustado"])
ax.set_xlabel("Categoria")
ax.set_ylabel("Valor Ajustado")

st.pyplot(fig)
