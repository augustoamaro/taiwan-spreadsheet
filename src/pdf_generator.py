from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
import pandas as pd
import os
from typing import List


class PDFGenerator:
    """Classe responsável pela geração dos arquivos PDF."""

    def __init__(self, output_dir: str = "relatorios"):
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        # Cria um estilo personalizado para o título
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            alignment=1  # Centralizado
        ))
        # Estilo para células da tabela
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontSize=7,  # Fonte ainda menor
            leading=8,   # Espaçamento entre linhas
            spaceBefore=0,
            spaceAfter=0,
        ))
        os.makedirs(output_dir, exist_ok=True)

    def _formatar_celula(self, valor) -> str:
        """Formata o valor da célula como Paragraph para permitir quebra de linha."""
        return Paragraph(str(valor), self.styles['TableCell'])

    def criar_pdf_por_cliente(self, df: pd.DataFrame, cliente: str) -> str:
        """Cria um PDF para um cliente específico."""
        dados_cliente = df[df['Cliente'] == cliente]

        # Define o nome do arquivo usando apenas o nome do cliente
        nome_arquivo = "".join(
            c for c in cliente if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = os.path.join(self.output_dir, f"{nome_arquivo}.pdf")

        # Cria o documento no formato paisagem com margens menores
        doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(letter),
            rightMargin=15,   # Margens ainda menores
            leftMargin=15,
            topMargin=20,
            bottomMargin=20
        )

        # Prepara os elementos do documento
        elementos = []

        # Adiciona título
        titulo = Paragraph(
            f"Relatório - {cliente}", self.styles['CustomTitle'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 10))

        # Prepara os dados da tabela com formatação
        headers = dados_cliente.columns.tolist()
        dados = [headers]

        # Formata cada célula para permitir quebra de linha
        for _, row in dados_cliente.iterrows():
            formatted_row = [self._formatar_celula(val) for val in row]
            dados.append(formatted_row)

        # Larguras ajustadas das colunas
        larguras_colunas = [
            0.7*inch,  # Item
            1.7*inch,  # Chassi
            1.7*inch,  # Modelo
            1.3*inch,  # Cliente
            1.1*inch,  # Cidade
            1.3*inch,  # Status Funcionamento
            1.7*inch,  # Manutenção
            0.6*inch,  # Quantidade
        ]

        # Cria a tabela com larguras específicas
        tabela = Table(dados, colWidths=larguras_colunas, repeatRows=1)

        # Estilo da tabela
        tabela.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5d7b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Fonte menor no cabeçalho
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),

            # Corpo da tabela
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),

            # Alinhamentos específicos
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Item
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Chassi
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),    # Modelo
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),    # Cliente
            ('ALIGN', (4, 0), (4, -1), 'LEFT'),    # Cidade
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),  # Status
            ('ALIGN', (6, 0), (6, -1), 'LEFT'),    # Manutenção
            ('ALIGN', (7, 0), (7, -1), 'CENTER'),  # Quantidade

            # Quebra de linha
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Grid mais fino
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

            # Zebra stripes mais suave
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f8f8'))
              for i in range(2, len(dados), 2)]
        ]))

        elementos.append(tabela)
        doc.build(elementos)

        return filename

    def gerar_pdfs_todos_clientes(self, df: pd.DataFrame) -> List[str]:
        """Gera PDFs para todos os clientes."""
        arquivos_gerados = []
        for cliente in df['Cliente'].unique():
            arquivo = self.criar_pdf_por_cliente(df, cliente)
            arquivos_gerados.append(arquivo)
        return arquivos_gerados
