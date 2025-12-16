import os
import pandas as pd

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
    Lê um ficheiro PS2 e devolve um dicionário estruturado.
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
                objDebitoDireto = {
                    'data': linha[1:9], 
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
    Lê todos os ficheiros .ps2 e devolve um DataFrame Pandas.
    """
    lista_final = []

    if not os.path.exists(caminho_pasta):
        print(f"Erro: Pasta não encontrada: {caminho_pasta}")
        return pd.DataFrame()

    for ficheiro in os.listdir(caminho_pasta):
        if ficheiro.endswith(".ps2"):
            path_completo = os.path.join(caminho_pasta, ficheiro)
            dados = ler_ficheiro(path_completo)
            
            if dados and 'data' in dados:
                data_proc = dados['data']
                
                for mov in dados.get('movimentos', []):
                    lista_final.append({
                        "data": data_proc,
                        "cliente_nib": mov['nib'],
                        "descricao": mov['descricao'],
                        "valor": mov['valor'],
                        "ordem": mov['ordem']
                    })

    df = pd.DataFrame(lista_final)

    # Converter datas para o formato correto do Pandas
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], format='%Y%m%d', errors='coerce')
    
    return df

# --- BLOCO DE PROTEÇÃO ---
# Isto impede que o código corra sozinho quando é importado pelo app.py
if __name__ == "__main__":
    print("--- Teste do Parser ---")
    # Para testar, ajusta o caminho se necessário
    # df = processar_toda_pasta('../data')
    # print(df.head())
