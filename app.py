import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Veloz Connect - Controle de Gastos", page_icon="📊", layout="wide")

# Inicialização do Banco de Dados com dados de teste
if 'gastos_diarios' not in st.session_state:
    dados_iniciais = [
        {'Data': pd.to_datetime('2026-10-01'), 'Tipo': 'Gastos Diários (Variáveis)', 'Categoria': 'Gasolina', 'Descricao': 'Posto Central - Manutenção', 'Valor': 250.00, 'Colaborador/Fornecedor': 'Josue'},
        {'Data': pd.to_datetime('2026-10-02'), 'Tipo': 'Gastos Diários (Variáveis)', 'Categoria': 'Almoço', 'Descricao': 'Almoço equipe em campo', 'Valor': 120.00, 'Colaborador/Fornecedor': 'Equipe Externa'},
        {'Data': pd.to_datetime('2026-10-03'), 'Tipo': 'Gastos Diários (Variáveis)', 'Categoria': 'Diárias Pagas', 'Descricao': 'Hospedagem visita técnica', 'Valor': 300.00, 'Colaborador/Fornecedor': 'Técnico Campo'},
        {'Data': pd.to_datetime('2026-10-05'), 'Tipo': 'Gastos Fixos', 'Categoria': 'Boletos e Contas', 'Descricao': 'Link Dedicado de Internet', 'Valor': 1500.00, 'Colaborador/Fornecedor': 'Operadora Backbone'},
        {'Data': pd.to_datetime('2026-10-05'), 'Tipo': 'Gastos Fixos', 'Categoria': 'Fornecedores', 'Descricao': 'Compra de Cabos e Conectores', 'Valor': 850.00, 'Colaborador/Fornecedor': 'Coelho Tecnologia'},
        {'Data': pd.to_datetime('2026-10-05'), 'Tipo': 'Gastos Fixos', 'Categoria': 'Salários de Funcionários', 'Descricao': 'Pagamento Operacional', 'Valor': 4500.00, 'Colaborador/Fornecedor': 'Folha de Pagamento'}
    ]
    st.session_state.gastos_diarios = pd.DataFrame(dados_iniciais)

# Logotipo na Barra Lateral (Sidebar)
st.sidebar.image("logo.jpg", use_column_width=True)

# Título Principal
st.title("Veloz Connect - Sistema de Controle de Gastos Mensais")
st.markdown("Gerenciamento completo de despesas diárias, custos fixos e folha de pagamento.")

st.sidebar.markdown("---")
st.sidebar.header("Painel de Navegação")
menu = st.sidebar.radio("Escolha uma opção:", ["Lançamento de Gastos", "Dashboard e Gráficos", "Relatórios Detalhados"])

# 1. LANÇAMENTO DE GASTOS
if menu == "Lançamento de Gastos":
    st.header("📝 Inserir Informações de Gastos")
    with st.form("form_gastos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_gasto = st.date_input("Data do Gasto")
            tipo_gasto = st.selectbox("Tipo de Gasto", ["Gastos Diários (Variáveis)", "Gastos Fixos"])
        with col2:
            if tipo_gasto == "Gastos Diários (Variáveis)":
                categoria = st.selectbox("Categoria", ["Gasolina", "Almoço", "Diárias Pagas", "Outros Diários"])
            else:
                categoria = st.selectbox("Categoria", ["Boletos e Contas", "Fornecedores", "Salários de Funcionários", "Outros Fixos"])
            descricao = st.text_input("Descrição / Observação", placeholder="Ex: Viagem para manutenção...")
        col3, col4 = st.columns(2)
        with col3:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=10.0)
        with col4:
            beneficiario = st.text_input("Responsável / Fornecedor / Funcionário")
        submitted = st.form_submit_button("Salvar Lançamento")
        if submitted and valor > 0:
            novo_registro = pd.DataFrame([{
                'Data': pd.to_datetime(data_gasto),
                'Tipo': tipo_gasto,
                'Categoria': categoria,
                'Descricao': descricao,
                'Valor': valor,
                'Colaborador/Fornecedor': beneficiario
            }])
            st.session_state.gastos_diarios = pd.concat([st.session_state.gastos_diarios, novo_registro], ignore_index=True)
            st.success("Gasto registrado com sucesso!")

# 2. DASHBOARD E GRÁFICOS
elif menu == "Dashboard e Gráficos":
    st.header("📊 Painel Analítico e Gráficos")
    df = st.session_state.gastos_diarios
    if not df.empty:
        total_geral = df['Valor'].sum()
        total_diarios = df[df['Tipo'] == 'Gastos Diários (Variáveis)']['Valor'].sum()
        total_fixos = df[df['Tipo'] == 'Gastos Fixos']['Valor'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Gasto Total", f"R$ {total_geral:,.2f}")
        col2.metric("🚗 Gastos Diários", f"R$ {total_diarios:,.2f}")
        col3.metric("🏢 Gastos Fixos e Salários", f"R$ {total_fixos:,.2f}")
        
        st.markdown("---")
        df_cat = df.groupby('Categoria')['Valor'].sum().reset_index().sort_values(by="Valor", ascending=False)
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("🔻 Visão em Pirâmide (Funil de Gastos)")
            fig_funnel = px.funnel(df_cat, x='Valor', y='Categoria', title="Distribuição de Custos por Categoria", color='Categoria')
            fig_funnel.update_layout(showlegend=False)
            st.plotly_chart(fig_funnel, use_container_width=True)
        with col_g2:
            st.subheader("🍩 Distribuição Percentual (Rosca)")
            fig_pie = px.pie(df_cat, names='Categoria', values='Valor', title="Participação por Categoria de Gasto", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

# 3. RELATÓRIOS DETALHADOS
elif menu == "Relatórios Detalhados":
    st.header("📋 Histórico Completo de Lançamentos")
    df = st.session_state.gastos_diarios
    if not df.empty:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos", "Gastos Diários (Variáveis)", "Gastos Fixos"])
        df_filtrado = df if filtro_tipo == "Todos" else df[df['Tipo'] == filtro_tipo]
        st.dataframe(df_filtrado, use_container_width=True)
        if st.button("🗑️ Limpar Todos os Dados"):
            st.session_state.gastos_diarios = pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Descricao', 'Valor', 'Colaborador/Fornecedor'])
            st.rerun()
