import os
import pandas as pd
import re  # Biblioteca para ler padrões de texto (Regex)

def converter_int(valor_str):
    try:
        return int(valor_str)
    except ValueError:
        return 0

def converter_euros(valor_str):
    try:
        valor_int = int(valor_str)
        valor_float = valor_int / 100.0
        return valor_float
    except ValueError:
        return 0.0

def ler_ficheiro(path):
    """
    Lê o conteúdo interno do ficheiro PS2.
    """
    objDebitoDireto = {}
    
    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf-8") as f:
        for linha in f:
            if linha.startswith('1'):
                # Cabeçalho
                objEmpresa = { 'designacao': linha[9:52].strip(), 'nif': linha[52:62].strip() }
                objResumo = {
                    'valorTotal': converter_euros(linha[62:75]),
                    'quantidade': converter_int(linha[75:81]) 
                }
                # Lemos a data interna, mas vamos ignorá-la se o nome do ficheiro for válido
                objDebitoDireto = {
                    'data_interna': linha[1:9], 
                    'empresa': objEmpresa, 
                    'resumo': objResumo,
                    'movimentos': [] 
                }
                
            elif linha.startswith('2'):
                # Movimento
                if 'movimentos' in objDebitoDireto:
                    objMovimento = { 
                        'ordem': linha[8:11], 
                        'nib': linha[11:41],
                        'valor': converter_euros(linha[41:55]),
                        'descricao': linha[55:82].strip() 
                    }
                    objDebitoDireto['movimentos'].append(objMovimento)

    return objDebitoDireto

def processar_toda_pasta(caminho_pasta):
    """
    Lê ficheiros e usa o NOME do ficheiro para definir a data.
    """
    lista_final = []

    if not os.path.exists(caminho_pasta):
        print(f"Erro: Pasta não encontrada: {caminho_pasta}")
        return pd.DataFrame()

    for ficheiro in os.listdir(caminho_pasta):
        if ficheiro.endswith(".ps2"):
            path_completo = os.path.join(caminho_pasta, ficheiro)
            dados = ler_ficheiro(path_completo)
            
            # --- LÓGICA NOVA: Extrair data do nome do ficheiro ---
            # Procura padrão: DD_ + 4 digitos (ano) + _ + 2 digitos (mes)
            match = re.search(r"DD_(\d{4})_(\d{2})", ficheiro)
            
            if match:
                ano = match.group(1) # ex: 2025
                mes = match.group(2) # ex: 01
                # Forçamos o dia 01 para ficar ordenado no gráfico
                data_final = f"{ano}{mes}01" 
            else:
                # Se o nome do ficheiro não tiver data, usa a do cabeçalho
                data_final = dados.get('data_interna', '20250101')

            if dados and 'movimentos' in dados:
                nif_empresa = dados['empresa']['nif']
                
                for mov in dados['movimentos']:
                    lista_final.append({
                        "data": data_final,  # Agora usa a data do nome do ficheiro
                        "entidade_nif": nif_empresa,
                        "cliente_nib": mov['nib'],
                        "descricao": mov['descricao'],
                        "valor": mov['valor'],
                        "ordem": mov['ordem']
                    })

    df = pd.DataFrame(lista_final)

    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], format='%Y%m%d', errors='coerce')
    
    return df

if __name__ == "__main__":
    print("--- Teste do Parser ---")
    # df = processar_toda_pasta('../data')
    # print(df.head())
