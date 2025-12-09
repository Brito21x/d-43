def converter_int(valor_str ):
        return   int( valor_str)

def converter_euros(valor_str ):
        valor_int =  int( valor_str)
        valor_float =  valor_int / 100.0
        return valor_float

def ler_ficheiro(path):
    objDebitoDireto = {}
    with open(path, encoding="utf-8") as f:
        for linha in f:
            # print(linha, end='')
            if linha[0] == '1':
                # print('----- cabeçalho')
                # print('data=',    linha[1:9])
                # print('empresa=', linha[9:39]) #  repr(linha[9:39]) # 'IPCA Energy                   '
                # print('nif=',     linha[39:48])
                # print('total=',   linha[48:62])
                # print('nº movimentos=',   linha[62:68])
                #objEmpresa = { 'designacao': linha[9:39], 'nif': linha[39:48]  }
                objEmpresa = { 'designacao': linha[9:52], 'nif': linha[52:62]  }
                #objResumo = {'valorTotal': converter_euros( linha[48:62]),
                #             'quantidade': converter_int(linha[62:68] ) }
                objResumo = {'valorTotal': converter_euros( linha[62:75]),
                             'quantidade': converter_int(linha[75:81] ) }
                objDebitoDireto = {'data': linha[1:9], 'empresa': objEmpresa, 'resumo': objResumo,
                                    'movimentos': [] }
                #print(objDebitoDireto)
            elif linha[0] == '2':
                print('------ movimento')
                #valor_str =  linha[41:55]
                #valor_int =  int( valor_str)
                #valor_float =  valor_int / 100.0
                # objMovimento = { 'ordem': linha[8:11], 'nib': linha[11:41], 'valor': linha[41:55], 'descricao': linha[55:82]  }
                #objMovimento = { 'ordem': linha[8:11], 'nib': linha[11:41], 'valor': valor_int, 'descricao':   linha[55:82] }
                #objMovimento = { 'ordem': linha[8:11], 'nib': linha[11:41], 'valor': valor_float, 'descricao':   linha[55:82] }
                objMovimento = { 'ordem': linha[8:11], 'nib': linha[11:41],
                                 'valor': converter_euros(linha[41:55]),
                                 'descricao':   linha[55:82] }
                objDebitoDireto['movimentos'].append(objMovimento)
            elif linha[0] == '9':
                print('------ fecho')

    return objDebitoDireto

# --
resultado = ler_ficheiro('../data/DD_2025_09.ps2')
print(resultado)

# --
resultado = ler_ficheiro('../data/DD_2025_10.ps2')
print(resultado)

