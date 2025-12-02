import os
import json
from decimal import Decimal
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# --- CONSTANTES DE MAPEAMENTO ---

# Traduz os códigos numéricos para a descrição do serviço
DESCRICAO_OPERACOES = {
    # Pagamentos (Códigos < 50)
    1: "Água", 2: "Gás", 3: "Electricidade", 4: "Gás/Electricidade",
    5: "Telefone", 6: "Telex", 7: "Renda de casa", 8: "Ordenados",
    9: "Fornecedores", 12: "Transferência",
    # Recebimentos (Códigos >= 50)
    51: "Água", 52: "Gás", 53: "Electricidade", 54: "Gás/Electricidade",
    55: "Telefone", 56: "Telex", 57: "Renda de casa", 58: "Serviço Público Terrestre",
    59: "Fornecedores", 60: "Seguro", 61: "Quotas", 62: "Transferência",
    64: "Cobrança", 66: "Serviços Diversos", 71: "Reembolso IVA",
    98: "Outros"
}

# Traduz os códigos de retorno para o estado da transação
ESTADOS_CONTA = {
    "00": "Sucesso (Lançamento Executado)",
    "01": "Não existe autorização de débito",
    "02": "Recusa de débito pelo banco",
    "03": "Conta sem saldo ou saldo insuficiente",
    "04": "Conta inexistente",
    "05": "Registo inválido",
    "06": "Cancelamento pelo cliente",
    "18": "Autorização Caducada",
    "20": "Suspensão"
}

@dataclass
class PS2Operacao:
    """
    Estrutura de dados para armazenar os detalhes de uma operação (Registo Tipo 2).
    """
    linha_num: int
    tipo_operacao_cod: int
    tipo_operacao_desc: str
    natureza: str           # 'PAGAMENTO' ou 'RECEBIMENTO'
    valor: float            # Valor absoluto
    valor_sinalizado: float # Negativo para saídas, positivo para entradas
    
    # Dados Bancários
    nib_completo: str
    banco: str
    balcao: str
    conta: str
    
    # Estado e Referências
    situacao_cod: str
    situacao_desc: str
    referencia_empresa: str
    referencia_transferencia: str
    adc_numero: Optional[str] = None # Número de Autorização de Débito em Conta
    
    sucesso: bool = True

class PS2Parser:
    def __init__(self, pasta_dados: str):
        self.pasta_dados = pasta_dados
        self.registos: List[Dict] = []
        self.erros: List[str] = []

    def _ler_valor_monetario(self, texto: str) -> Decimal:
        """
        Converte string numérica (ex: '0000000024750') para Decimal,
        assumindo que os últimos 2 dígitos são casas decimais.
        """
        try:
            return Decimal(texto) / Decimal(100)
        except:
            return Decimal(0)

    def processar_linha_tipo_2(self, linha: str, num_linha: int) -> Optional[PS2Operacao]:
        """
        Processa uma linha de registo 'Tipo 2', extraindo campos por posição fixa.
        """
        try:
            # Extração posicional dos campos obrigatórios
            op_code = int(linha[4:6])
            situacao = linha[6:8]
            
            # Reconstrução do NIB
            banco = linha[9:13]
            balcao = linha[13:17]
            conta = linha[17:28]
            controlo = linha[28:30]
            nib = f"{banco}{balcao}{conta}{controlo}"
            
            # Conversão do valor monetário
            valor_raw = linha[30:43]
            valor_dec = self._ler_valor_monetario(valor_raw)
            
            # Extração de referências de texto
            ref_empresa = linha[43:63].strip()
            ref_transf = linha[63:78].strip()

            # Lógica: Natureza da Operação (Débito vs Crédito)
            # Códigos < 50 são Pagamentos (saída de dinheiro)
            # Códigos >= 50 são Recebimentos (entrada de dinheiro)
            if op_code < 50:
                natureza = "PAGAMENTO"
                valor_final = -float(valor_dec)
            else:
                natureza = "RECEBIMENTO"
                valor_final = float(valor_dec)

            # Lógica: Extração de ADC para Cobranças
            # Se for cobrança (>=50), as primeiras 11 posições da referência são o ADC
            adc = None
            if op_code >= 50 and len(ref_empresa) >= 11:
                adc = ref_empresa[:11].strip()

            # Definição do estado da transação
            estado_desc = ESTADOS_CONTA.get(situacao, f"Estado desconhecido ({situacao})")
            sucesso = (situacao == "00")

            return PS2Operacao(
                linha_num=num_linha,
                tipo_operacao_cod=op_code,
                tipo_operacao_desc=DESCRICAO_OPERACOES.get(op_code, "Outros"),
                natureza=natureza,
                valor=float(valor_dec),
                valor_sinalizado=valor_final,
                nib_completo=nib,
                banco=banco,
                balcao=balcao,
                conta=conta,
                situacao_cod=situacao,
                situacao_desc=estado_desc,
                referencia_empresa=ref_empresa,
                referencia_transferencia=ref_transf,
                adc_numero=adc,
                sucesso=sucesso
            )

        except Exception as e:
            self.erros.append(f"Linha {num_linha}: Erro ao processar registo Tipo 2 - {e}")
            return None

    def carregar_tudo(self) -> List[dict]:
        """
        Percorre a pasta configurada, lê todos os ficheiros .ps2 e retorna a lista consolidada.
        """
        todos_dados = []

        if not os.path.exists(self.pasta_dados):
            print(f"Erro: Pasta '{self.pasta_dados}' não encontrada.")
            return []

        for nome_arq in os.listdir(self.pasta_dados):
            if not nome_arq.endswith(".ps2"):
                continue

            caminho = os.path.join(self.pasta_dados, nome_arq)
            print(f"A processar: {nome_arq}...")

            # Acumuladores para validação do rodapé (checksum)
            soma_calculada = Decimal(0)
            count_calculado = 0
            
            try:
                # 'latin-1' é o padrão comum para ficheiros bancários antigos/legados
                with open(caminho, 'r', encoding='latin-1') as f:
                    for i, linha in enumerate(f):
                        linha = linha.strip('\n').strip('\r')
                        
                        # Ignora linhas que não comecem pelo identificador obrigatório
                        if not linha.startswith("PS2"):
                            continue

                        tipo = linha[3]

                        if tipo == '2':
                            # Processa detalhe
                            op = self.processar_linha_tipo_2(linha, i+1)
                            if op:
                                op_dict = asdict(op)
                                op_dict['ficheiro'] = nome_arq
                                todos_dados.append(op_dict)
                                
                                # Atualiza acumuladores
                                soma_calculada += Decimal(str(op.valor))
                                count_calculado += 1
                        
                        elif tipo == '9':
                            # Processa rodapé e valida integridade
                            qtd_total_ps2 = int(linha[15:29])
                            valor_total_ps2 = Decimal(linha[29:42]) / Decimal(100)
                            
                            if count_calculado != qtd_total_ps2:
                                self.erros.append(f"{nome_arq}: Erro contagem (Lido: {count_calculado} vs Header: {qtd_total_ps2})")
                            
                            if soma_calculada != valor_total_ps2:
                                self.erros.append(f"{nome_arq}: Erro soma valor (Lido: {soma_calculada} vs Header: {valor_total_ps2})")

            except Exception as e:
                self.erros.append(f"Erro fatal em {nome_arq}: {e}")

        # Exibe erros acumulados no final do processamento
        if self.erros:
            print("\n⚠️ AVISOS DE PROCESSAMENTO:")
            for erro in self.erros:
                print(f" - {erro}")

        return todos_dados

# --- TESTE UNITÁRIO ---
if __name__ == "__main__":
    parser = PS2Parser("data")
    dados = parser.carregar_tudo()

    if dados:
        print(f"\n✅ Processamento concluído. {len(dados)} registos extraídos.")
        
        # Filtra rejeições
        rejeicoes = [d for d in dados if not d['sucesso']]
        if rejeicoes:
            print(f"\n❌ ATENÇÃO: {len(rejeicoes)} operações com erro/rejeitadas:")
            for rej in rejeicoes:
                print(f"   - Linha {rej['linha_num']}: {rej['situacao_desc']} | Valor: {rej['valor']}€")

        # Calcula saldo (apenas sucessos)
        saldo = sum(d['valor_sinalizado'] for d in dados if d['sucesso'])
        print(f"\n💰 SALDO LÍQUIDO (Sucessos): {saldo:.2f} €")
        
        # Mostra exemplo da estrutura
        if len(dados) > 0:
            print("\n🔍 Exemplo de Registo Completo:")
            print(json.dumps(dados[0], indent=2, ensure_ascii=False))
