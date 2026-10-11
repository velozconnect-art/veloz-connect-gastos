import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Veloz Connect - Controle de Gastos", page_icon="📊", layout="wide")

# Inicialização do Banco de Dados Vazio
if 'gastos_diarios' not in st.session_state:
    st.session_state.gastos_diarios = pd.DataFrame(columns=[
        'Data', 'Tipo', 'Categoria', 'Descricao', 'Valor', 'Colaborador/Fornecedor'
    ])

# Logotipo na Barra Lateral (Sidebar)
try:
    st.sidebar.image("logo.jpg", use_column_width=True)
except:
    pass

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
                categoria = st.selectbox("Categoria", ["Salario","Fornecedores","Boletos","Outros Fixos"])
            
            descricao = st.text_input("Descrição / Observação", placeholder="Ex: Viagem para manutenção...")
        
        col3, col4 = st.columns(2)
        with col3:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=10.0)
        with col4:
            if tipo_gasto == "Gastos Fixos" and categoria == "Fornecedores":
                beneficiario = st.selectbox("Selecione o Fornecedor", [
                    "GW",
                    "BR DISTRIBUIDORA",
                    "C2 CONECT",
                    "OIW",
                    "DNT",
                    "INTELBRAS",
                    "SEGCOM",
                    "SOMAR DISTRIBUIDORA",
                    "DDTELECOM",
                    "Outros"
                ])
            elif tipo_gasto == "Gastos Fixos" and categoria == "SALARIO":
                beneficiario = st.selectbox("Selecione o Funcionário", [
                    "Jo Morais",
                    "Josue Morais",
                    "Jona de Jesus",
                    "Outro"
                ])
            else:
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
            st.subheader("🧊 Visão 3D de Custos por Categoria")
            fig_3d = px.bar(
                df_cat, 
                x='Categoria', 
                y='Valor', 
                color='Categoria', 
                text='Valor',
                title="Distribuição Tridimensional de Custos"
            )
            fig_3d.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
            fig_3d.update_layout(showlegend=False, scene=dict(xaxis_title='Categoria', yaxis_title='Valor'))
            st.plotly_chart(fig_3d, use_container_width=True)
            
        with col_g2:
            st.subheader("Distribuição Percentual")
            fig_pie = px.pie(df_cat, names='Categoria', values='Valor', title="Participação por Categoria de Gasto", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Ainda não há dados lançados. Vá até a aba 'Lançamento de Gastos' para adicionar as despesas.")

# 3. RELATÓRIOS DETALHADOS E EXCLUSÃO INDIVIDUAL SEGURA
elif menu == "Relatórios Detalhados":
    st.header("📋 Histórico Completo e Gestão de Lançamentos")
    df = st.session_state.gastos_diarios
    
    if not df.empty:
        st.info("💡 Cada linha tem um número de ID único. Insira exatamente o ID do registo que deseja apagar.")
        
        df_tabela = df.copy()
        df_tabela.insert(0, 'ID_Registo', range(1, len(df_tabela) + 1))
        
        st.dataframe(df_tabela, use_container_width=True)
        
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            id_para_apagar = st.selectbox("Selecione o ID da linha para apagar", options=list(range(1, len(df) + 1)))
            if st.button("❌ Apagar Apenas este Registo"):
                indice_real = id_para_apagar - 1
                st.session_state.gastos_diarios = df.drop(df.index[indice_real]).reset_index(drop=True)
                st.success(f"Registo ID {id_para_apagar} apagado com sucesso!")
                st.rerun()
                
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Limpar Todos os Registos"):
                st.session_state.gastos_diarios = pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Descricao', 'Valor', 'Colaborador/Fornecedor'])
                st.success("Todos os dados foram limpos!")
                st.rerun()
    else:
        st.info("Nenhum registro cadastrado no momento.")
