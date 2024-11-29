import pandas as pd
from typing import List, Dict


class DataProcessor:
    """Classe responsável pelo processamento dos dados da planilha."""

    def __init__(self):
        self.df = None
        self.colunas_esperadas = [
            'Item', 'Chassi', 'Modelo', 'Cliente', 'Cidade',
            'Status Funcionamento', 'Manutenção', 'Quantidade'
        ]

    def validar_colunas(self, df: pd.DataFrame) -> tuple[bool, str]:
        """Valida se todas as colunas necessárias estão presentes."""
        colunas_atuais = [
            col for col in df.columns if not col.startswith('Unnamed')]
        colunas_faltantes = [
            col for col in self.colunas_esperadas if col not in colunas_atuais]
        if colunas_faltantes:
            return False, f"Colunas faltantes: {', '.join(colunas_faltantes)}"
        return True, "Todas as colunas estão presentes"

    def processar_arquivo(self, arquivo) -> tuple[bool, str]:
        """Processa o arquivo Excel enviado."""
        try:
            # Primeiro, vamos ler todas as linhas do arquivo para debug
            df_temp = pd.read_excel(arquivo, header=None)

            # Tenta encontrar a linha do cabeçalho procurando pela palavra "item"
            header_row = None
            for idx, row in df_temp.iterrows():
                row_values = [str(val).lower().strip()
                              for val in row.values if pd.notna(val)]
                if 'item' in row_values:
                    header_row = idx
                    break

            if header_row is None:
                return False, "Não foi possível encontrar a linha de cabeçalho com 'Item'"

            # Lê o arquivo novamente usando a linha correta como cabeçalho
            self.df = pd.read_excel(arquivo, header=header_row)

            # Remove colunas vazias
            self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]

            # Normaliza os nomes das colunas
            self.df.columns = [str(col).strip() for col in self.df.columns]

            # Filtra apenas as colunas que precisamos
            colunas_presentes = [
                col for col in self.colunas_esperadas if col in self.df.columns]
            self.df = self.df[colunas_presentes]

            # Remove linhas vazias
            self.df = self.df.dropna(how='all')

            # Converte todas as colunas para string
            for coluna in self.df.columns:
                if coluna != 'Quantidade':
                    self.df[coluna] = self.df[coluna].astype(str)

            # Adiciona numeração sequencial apenas para a coluna Quantidade
            self.df['Quantidade'] = range(1, len(self.df) + 1)

            # Reordena as colunas conforme a ordem esperada
            self.df = self.df.reindex(columns=self.colunas_esperadas)

            valido, mensagem = self.validar_colunas(self.df)
            if not valido:
                return False, f"Erro na validação das colunas: {mensagem}\nColunas encontradas: {list(self.df.columns)}"

            return True, "Arquivo processado com sucesso!"
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return False, f"Erro ao processar arquivo: {str(e)}"

    def get_valores_unicos(self, coluna: str) -> List:
        """Retorna valores únicos de uma coluna."""
        try:
            if self.df is not None and coluna in self.df.columns:
                valores = self.df[coluna].unique()
                # Remove valores nulos/vazios
                valores = [str(val).strip() for val in valores if pd.notna(
                    val) and str(val).strip()]
                return sorted(valores)
            return []
        except Exception as e:
            print(f"Erro ao obter valores únicos da coluna {coluna}: {str(e)}")
            return []

    def filtrar_dados(self, filtros: Dict) -> pd.DataFrame:
        """Aplica filtros ao DataFrame."""
        try:
            df_filtrado = self.df.copy()
            for coluna, valor in filtros.items():
                if valor:
                    # Converte os valores do filtro para string para compatibilidade
                    valores_filtro = [str(v) for v in valor]
                    df_filtrado = df_filtrado[df_filtrado[coluna].isin(
                        valores_filtro)]

            # Atualiza apenas a coluna Quantidade após a filtragem
            df_filtrado['Quantidade'] = range(1, len(df_filtrado) + 1)

            return df_filtrado
        except Exception as e:
            print(f"Erro ao aplicar filtros: {str(e)}")
            return self.df.copy()
