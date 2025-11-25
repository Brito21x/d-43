# Ficheiro: src/parser.py (Adicionar o código abaixo)

from typing import List

def carregar_todos_ps2(pasta_dados: str = "data") -> List[dict]:
    """
    Percorre a pasta de dados, lê todos os ficheiros PS2 e junta as operações.
    Args:pasta_dados (str): O caminho para a pasta que contém os ficheiros PS2.
    Returns:
    List[dict]: Uma lista única de todos os registos de detalhe (Tipo 2) de todos os ficheiros.
    """
    todos_registos = []
    
    # 1. Percorre a pasta especificada
    for nome_ficheiro in os.listdir(pasta_dados):
        # 2. Verifica se o ficheiro termina em .ps2 (Regra do enunciado)
        if nome_ficheiro.endswith(".ps2"):
            # 3. Constrói o caminho completo para o ficheiro
            caminho_completo = os.path.join(pasta_dados, nome_ficheiro)
            
            print(f"Lendo ficheiro: {nome_ficheiro}...")
            
            # 4. Usa a tua função de parsing para ler o ficheiro
            dados_ficheiro = ler_ficheiro_ps2(caminho_completo)
            
            # 5. Adiciona apenas as operações (Tipo 2) à lista total
            if 'operacoes' in dados_ficheiro:
                # Adiciona o nome do ficheiro (mês/ano) a cada registo para permitir a filtragem no Shiny
                for operacao in dados_ficheiro['operacoes']:
                    operacao['ficheiro_origem'] = nome_ficheiro
                
                todos_registos.extend(dados_ficheiro['operacoes'])
            
            # (Opcional) Poderias adicionar aqui uma verificação de consistência usando 'dados_ficheiro["metadados"]'

    return todos_registos

2. 🧪 Testar a Nova Função

Agora, vamos mudar o bloco de teste (if __name__ == "__main__":) para usar a nova função.

Substitui o bloco if __name__ == "__main__": existente no teu src/parser.py pelo seguinte:
Python

# --- NOVO BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    
    # ⚠️ Certifica-te que o ficheiro de teste está em 'data/DD_2025_10.ps2'
    PASTA_DADOS = "data" 
    
    print(f"--- A carregar e processar todos os ficheiros da pasta: {PASTA_DADOS} ---")
    
    # Chama a nova função
    dados_totais_operacoes = carregar_todos_ps2(PASTA_DADOS)
    
    if dados_totais_operacoes:
        print(f"\nTotal de {len(dados_totais_operacoes)} operações encontradas em todos os ficheiros.")
        
        # Exemplo de Análise Global:
        total_global = sum(op['valor'] for op in dados_totais_operacoes)
        print(f"VALOR TOTAL GLOBAL DE DÉBITOS: {total_global:.2f} €")
        
        # Para ver a estrutura:
        print("\nPrimeiras 2 operações processadas:")
        print(json.dumps(dados_totais_operacoes[:2], indent=2, ensure_ascii=False))
        
    else:
        print("Nenhum ficheiro PS2 encontrado ou erro de leitura.")
