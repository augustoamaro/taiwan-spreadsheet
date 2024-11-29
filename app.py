import streamlit as st
from src.data_processor import DataProcessor
from src.pdf_generator import PDFGenerator
import zipfile
import os
import pandas as pd


def configurar_pagina():
    """Configura o tema e layout da página."""
    st.set_page_config(
        page_title="Sistema de Gestão de Dados",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto"
    )

    # Estilo CSS personalizado atualizado
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5rem 1rem;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            opacity: 0.85;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .upload-text {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .stAlert {
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)


def mostrar_instrucoes():
    """Mostra instruções de uso quando nenhum arquivo está carregado."""
    st.markdown("""
    
    Para começar:
    1. 📁 Faça upload de um arquivo Excel (.xlsx)
    2. 🔍 Use os filtros para analisar os dados
    3. 📊 Visualize as informações na tabela
    4. 📑 Gere PDFs individuais por cliente
    
    O arquivo Excel deve conter as seguintes colunas:
    - Item
    - Chassi
    - Modelo
    - Cliente
    - Cidade
    - Status Funcionamento
    - Manutenção
    - Quantidade
    """)


def main():
    configurar_pagina()

    # Cabeçalho com ícone
    st.markdown("# 📊 Sistema de Gestão de Dados")
    st.markdown("---")

    # Inicializa o processador de dados
    if 'processor' not in st.session_state:
        st.session_state.processor = DataProcessor()

    # Upload do arquivo
    col_upload, col_info = st.columns([2, 3])
    with col_upload:
        arquivo = st.file_uploader(
            "📁 Selecione o arquivo Excel",
            type=['xlsx'],
            help="Faça upload de um arquivo Excel (.xlsx) contendo os dados necessários"
        )

    if arquivo is not None:
        with col_info:
            st.info(f"📄 Arquivo carregado: {arquivo.name}")

        sucesso, mensagem = st.session_state.processor.processar_arquivo(
            arquivo)

        if sucesso:
            st.success("✅ " + mensagem)

            # Container para os filtros
            with st.container():
                st.markdown("### 🔍 Filtros de Dados")
                col1, col2, col3, col4 = st.columns(4)

                filtros = {}

                with col1:
                    clientes = st.multiselect(
                        "👥 Cliente",
                        st.session_state.processor.get_valores_unicos(
                            "Cliente"),
                        help="Selecione um ou mais clientes"
                    )
                    filtros["Cliente"] = clientes

                with col2:
                    cidades = st.multiselect(
                        "🏢 Cidade",
                        st.session_state.processor.get_valores_unicos(
                            "Cidade"),
                        help="Selecione uma ou mais cidades"
                    )
                    filtros["Cidade"] = cidades

                with col3:
                    status = st.multiselect(
                        "📊 Status Funcionamento",
                        st.session_state.processor.get_valores_unicos(
                            "Status Funcionamento"),
                        help="Selecione um ou mais status"
                    )
                    filtros["Status Funcionamento"] = status

                with col4:
                    manutencao = st.multiselect(
                        "🔧 Manutenção",
                        st.session_state.processor.get_valores_unicos(
                            "Manutenção"),
                        help="Selecione um ou mais tipos de manutenção"
                    )
                    filtros["Manutenção"] = manutencao

            # Aplica os filtros e mostra os dados
            df_filtrado = st.session_state.processor.filtrar_dados(filtros)

            # Informações sobre os dados filtrados
            total_registros = len(df_filtrado)
            total_clientes = len(df_filtrado['Cliente'].unique())

            # Métricas
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("Total de Registros", total_registros)
            with col_metric2:
                st.metric("Total de Clientes", total_clientes)

            # DataFrame com dados filtrados
            st.markdown("### 📋 Dados Filtrados")
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                height=500
            )

            # Botão para gerar PDFs
            st.markdown("### 📑 Geração de PDFs")
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

            with col_btn2:
                if st.button("📄 Gerar PDFs por Cliente", use_container_width=True):
                    with st.spinner('🔄 Gerando PDFs... Por favor, aguarde...'):
                        pdf_gen = PDFGenerator()
                        arquivos = pdf_gen.gerar_pdfs_todos_clientes(
                            df_filtrado)

                        # Cria ZIP
                        with zipfile.ZipFile("relatorios.zip", 'w') as zipf:
                            for arquivo in arquivos:
                                zipf.write(arquivo, os.path.basename(arquivo))

                        # Download
                        with open("relatorios.zip", "rb") as f:
                            st.download_button(
                                "⬇️ Baixar PDFs",
                                f,
                                "relatorios.zip",
                                "application/zip",
                                use_container_width=True
                            )
                            st.success(
                                f"✅ {total_clientes} PDFs gerados com sucesso!")
        else:
            st.error("❌ " + mensagem)
    else:
        mostrar_instrucoes()


if __name__ == "__main__":
    main()
