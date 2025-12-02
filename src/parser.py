import os
import json
from decimal import Decimal
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# --- TABELAS DE DOMÍNIO ---

# Mapeia os códigos numéricos de operação para a sua descrição textual
DESCRICAO_OPERACOES = {
    # Códigos < 50: Pagamentos (Débitos)
    1: "Água", 2: "Gás", 3: "Electricidade", 4: "Gás/Electricidade",
    5: "Telefone", 7: "Renda de casa", 8: "Ordenados", 9: "Fornecedores", 12: "Transferência",
    # Códigos >= 50: Recebimentos (Créditos)
    51: "Água", 52: "Gás", 53: "Electricidade", 54: "Gás/Electricidade",
    55: "Telefone", 58: "Serviço Público", 60: "Seguro", 64: "Cobrança", 98: "Outros"
}

# Mapeia os códigos de estado para a descrição do resultado da transação
ESTADOS_CONTA = {
    "00": "Sucesso", "01": "Sem Autorização", "02": "Recusa Banco",
    "03": "Saldo Insuficiente", "04": "Conta Inexistente", "05": "Registo Inválido",
    "06": "Cancelamento Cliente", "20": "Suspensão"
}

@dataclass
class PS2Operacao:
    """
    Estrutura de dados unificada que combina o contexto do ficheiro (Cabeçalho)
    com os detalhes da transação (Movimento).
    """
    # Contexto do Ficheiro (Origem: Registo Tipo 1)
    data_processamento: str
    entidade_ordenante: str
    
    # Detalhe da Operação (Origem: Registo Tipo 2)
    linha: int
    natureza: str           # 'PAGAMENTO' ou 'RECEBIMENTO'
    valor: float            # Valor absoluto para cálculos
    valor_sinalizado: float # Valor com sinal (- para débitos, + para créditos)
    descricao: str
    referencia_transf: str
    adc: Optional[str]      # Número da Autorização de Débito (apenas para Cobranças)
    
    # Dados Bancários
    nib_destino: str
    
    # Estado da Transação
    estado_cod: str
    estado_desc: str
    sucesso: bool

class PS2Parser:
    def __init__(self, pasta_dados: str):
        self.pasta_dados = pasta_dados
        self.erros: List[str] = []

    def _parse_decimal(self, val_str: str) -> Decimal:
        """Converte string financeira (sem ponto) para Decimal, assumindo 2 casas decimais."""
        try:
            return Decimal(val_str) / Decimal(100)
        except:
            return Decimal(0)

    def processar_ficheiro(self, caminho_completo: str, nome_ficheiro: str) -> List[dict]:
        """
        Lê um ficheiro PS2 linha a linha, gerindo o estado (Cabeçalho -> Movimentos -> Rodapé).
        """
        registos_ficheiro = []
        
        # Variáveis de Estado (Preenchidas pelo Tipo 1)
        header_lido = False
        data_processamento = None
        entidade_ordenante = None
        
        # Acumuladores para Validação de Integridade (Verificados no Tipo 9)
        soma_valores = Decimal(0)
        contagem_registos = 0
        
        try:
            # Utiliza 'latin-1' para suportar caracteres acentuados comuns em ficheiros bancários
            with open(caminho_completo, 'r', encoding='latin-1') as f:
                for i, linha in enumerate(f):
                    linha = linha.strip('\n').strip('\r')
                    num_linha = i + 1

                    # Ignora linhas que não cumpram o formato base
                    if not linha.startswith("PS2"):
                        continue

                    tipo_registo = linha[3] # O tipo está na 4ª posição (índice 3)

                    # --- TIPO 1: CABEÇALHO (Contexto) ---
                    if tipo_registo == '1':
                        data_processamento = linha[33:41]
                        entidade_ordenante = linha[41:61].strip()
                        header_lido = True

                    # --- TIPO 2: MOVIMENTO (Detalhe) ---
                    elif tipo_registo == '2':
                        if not header_lido:
                            self.erros.append(f"{nome_ficheiro}: Registo de movimento encontrado sem cabeçalho prévio.")
                            continue

                        # Extração posicional dos campos
                        op_code = int(linha[4:6])
                        situacao = linha[6:8]
                        
                        # Reconstrução do NIB (Banco + Balcão + Conta + Controlo)
                        nib = f"{linha[9:13]}{linha[13:17]}{linha[17:28]}{linha[28:30]}"
                        
                        # Tratamento do Valor Monetário
                        valor_dec = self._parse_decimal(linha[30:43])
                        
                        # Referências textuais
                        ref_empresa = linha[43:63].strip()
                        ref_transf = linha[63:78].strip()

                        # Lógica de Negócio: Determinar Natureza (Pagamento vs Recebimento)
                        if op_code < 50:
                            natureza = "PAGAMENTO"
                            sinalizado = -float(valor_dec)
                        else:
                            natureza = "RECEBIMENTO"
                            sinalizado = float(valor_dec)

                        # Lógica Específica: Extração de ADC para Cobranças
                        adc_num = None
                        if op_code >= 50 and len(ref_empresa) >= 11:
                            adc_num = ref_empresa[:11].strip()

                        # Criação do Objeto Consolidado
                        op_obj = PS2Operacao(
                            data_processamento=data_processamento,
                            entidade_ordenante=entidade_ordenante,
                            linha=num_linha,
                            natureza=natureza,
                            valor=float(valor_dec),
                            valor_sinalizado=sinalizado,
                            descricao=ref_empresa,
                            referencia_transf=ref_transf,
                            adc=adc_num,
                            nib_destino=nib,
                            estado_cod=situacao,
                            estado_desc=ESTADOS_CONTA.get(situacao, "Desconhecido"),
                            sucesso=(situacao == "00")
                        )
                        
                        op_dict = asdict(op_obj)
                        op_dict['ficheiro_origem'] = nome_ficheiro
                        registos_ficheiro.append(op_dict)

                        # Atualiza acumuladores para validação final
                        soma_valores += valor_dec
                        contagem_registos += 1

                    # --- TIPO 9: RODAPÉ (Validação) ---
                    elif tipo_registo == '9':
                        total_qtd_declarada = int(linha[15:29])
                        total_val_declarado = self._parse_decimal(linha[29:42])

                        # Validação Cruzada: Comparar valores lidos com valores declarados
                        if contagem_registos != total_qtd_declarada:
                            self.erros.append(f"{nome_ficheiro}: Quantidade inconsistente (Lido: {contagem_registos} | Esperado: {total_qtd_declarada})")
                        
                        if soma_valores != total_val_declarado:
                            self.erros.append(f"{nome_ficheiro}: Valor total inconsistente (Lido: {soma_valores} | Esperado: {total_val_declarado})")

        except Exception as e:
            self.erros.append(f"Erro crítico ao processar {nome_ficheiro}: {str(e)}")
            
        return registos_ficheiro

    def carregar_tudo(self) -> List[dict]:
        """Percorre a diretoria alvo e processa todos os ficheiros .ps2 encontrados."""
        todos = []
        if not os.path.exists(self.pasta_dados):
            return []
            
        for f in os.listdir(self.pasta_dados):
            if f.endswith(".ps2"):
                caminho = os.path.join(self.pasta_dados, f)
                print(f"A processar: {f}...")
                todos.extend(self.processar_ficheiro(caminho, f))
        
        if self.erros:
            print("\n⚠️  AVISOS DE PROCESSAMENTO:")
            for e in self.erros: print(f" - {e}")
            
        return todos

# --- TESTE UNITÁRIO ---
if __name__ == "__main__":
    parser = PS2Parser("data")
    dados = parser.carregar_tudo()
    
    if dados:
        print(f"\n✅ Processamento Concluído.")
        print(f"Total de Registos Extraídos: {len(dados)}")
        
        # Exemplo de acesso aos dados consolidados
        primeiro = dados[0]
        print(f"Ficheiro de Origem: {primeiro['ficheiro_origem']}")
        print(f"Data de Processamento: {primeiro['data_processamento']}")
        print(f"Entidade: {primeiro['entidade_ordenante']}")
        
        # Cálculo de Saldo
        saldo = sum(d['valor_sinalizado'] for d in dados if d['sucesso'])
        print(f"Saldo Líquido (Operações com Sucesso): {saldo:.2f} €")
