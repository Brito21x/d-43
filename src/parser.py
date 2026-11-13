import os
import pandas as pd
import re

def converter_int(valor_str):
    try:
        return int(valor_str)
    except (ValueError, TypeError):
        return 0

def converter_euros(valor_str):
    try:
        valor_int = int(valor_str)
        valor_float = valor_int / 100.0
        return valor_float
    except (ValueError, TypeError):
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
            linha = linha.rstrip("\r\n")
            if linha.startswith('1'):
                objEmpresa = { 'designacao': linha[9:52].strip(), 'nif': linha[52:62].strip() }
                objResumo = {
                    'valorTotal': converter_euros(linha[62:75]),
                    'quantidade': converter_int(linha[75:81]) 
                }
                objDebitoDireto = {
                    'data_interna': linha[1:9], 
                    'empresa': objEmpresa, 
                    'resumo': objResumo,
                    'movimentos': [] 
                }
                
            elif linha.startswith('2'):
                if 'movimentos' in objDebitoDireto:
                    campo_identificacao = linha[11:41]
                    c_nif = campo_identificacao[:9]
                    c_nib = campo_identificacao[9:]

                    objMovimento = { 
                        'ordem': linha[8:11],
                        'nif': c_nif,
                        'nib': c_nib,
                        'valor': converter_euros(linha[41:55]),
                        'descricao': linha[55:82].strip() 
                    }
                    objDebitoDireto['movimentos'].append(objMovimento)

    return objDebitoDireto

def processar_toda_pasta(caminho_pasta):
    """
    Lê ficheiros e devolve DataFrame com NIF e NIB separados.
    """
    lista_final = []

    if not os.path.exists(caminho_pasta):
        print(f"Erro: Pasta não encontrada: {caminho_pasta}")
        return pd.DataFrame()

    for ficheiro in sorted(os.listdir(caminho_pasta)):
        if ficheiro.lower().endswith(".ps2"):
            path_completo = os.path.join(caminho_pasta, ficheiro)
            dados = ler_ficheiro(path_completo)
            
            match = re.search(r"DD_(\d{4})_(\d{2})", ficheiro)
            if match:
                ano = match.group(1)
                mes = match.group(2)
                data_final = f"{ano}{mes}01" 
            else:
                data_final = dados.get('data_interna', '20250101')

            if dados and 'movimentos' in dados:
                entidade_nif = dados['empresa']['nif']
                
                for mov in dados['movimentos']:
                    lista_final.append({
                        "data": data_final,
                        "entidade_nif": entidade_nif,
                        "cliente_nif": mov['nif'],
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
