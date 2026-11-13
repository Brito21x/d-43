# 📊 Dashboard de Débitos Diretos (PS2)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Shiny_for_Python-v1.0%2B-blue?logo=rstudio&logoColor=white" alt="Shiny for Python">
  <img src="https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Plotly-5.0%2B-3F4F75?logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/IPCA-LESI-009639" alt="IPCA LESI">
  <img src="https://img.shields.io/badge/Status-Concluído-success" alt="Status">
</p>

> **Unidade Curricular:** Laboratórios de Informática  
> **Curso:** Licenciatura em Engenharia de Sistemas Informáticos (*Regime Laboral*) — Ano Letivo 2025/2026  
> **Instituição:** Instituto Politécnico do Cávado e do Ave (IPCA)

---

## 📑 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Instalação e Execução](#-instalação-e-execução)
- [Especificação do Formato PS2](#-especificação-do-formato-ps2)
- [Demonstração](#-demonstração)
- [Equipa de Desenvolvimento](#-equipa-de-desenvolvimento)
- [Referências](#-referências)

---

## 🎯 Sobre o Projeto

O **Dashboard de Débitos Diretos** é uma solução de software desenvolvida para processar, validar e visualizar lotes mensais de débitos bancários diretos no formato proprietário **PS2** da entidade *IPCA Energy*.

A aplicação faz a ponte entre dados brutos de largura fixa e uma interface analítica interativa construída em **Shiny for Python**, permitindo aos operadores financeiros inspecionar KPIs globais, auditar movimentos de clientes e explorar tendências temporais de liquidação em tempo real.

---

## 🚀 Funcionalidades Principais

* **Parser de Ficheiros PS2:** Extração automática de dados posicionais a partir de ficheiros bancários (cabeçalhos, registos de movimentos e totalizadores).
* **Tratamento e Normalização de Dados:**
  * Separação rigorosa do identificador de 30 caracteres em **NIF (9 dígitos)** e **NIB (21 dígitos)**;
  * Conversão de valores monetários de cêntimos inteiros para euros decimais;
  * Resolução temporal com base no identificador de ficheiro e validação de consistência.
* **Dashboard Interativo e Reativo:**
  * **Filtros Dinâmicos:** Seleção flexível de intervalos de datas e filtragem seletiva por cliente (NIB);
  * **Indicadores Executivos (KPIs):** Total financeiro acumulado e contagem total de movimentos no período;
  * **Gráfico de Evolução Temporal:** Linha temporal interativa com marcadores e formatação monetária (Plotly);
  * **Top Clientes por Gasto:** Gráfico de barras ordenado com os maiores débitos acumulados;
  * **Tabela de Dados Detalhada:** Grelha paginada, ordenada cronologicamente, com espaçamento formatado para facilitar a leitura de NIFs e NIBs.

---

## 📁 Estrutura do Repositório

O projeto segue uma arquitetura limpa e modular:

```text
d-43/
├── assets/
│   └── img/
│       └── DashboardDebitos.png   # Imagens e capturas de ecrã do dashboard
├── data/                          # Dados de entrada (lotes mensais em formato PS2)
│   ├── DD_2025_01.ps2
│   └── ...
├── doc/                           # Documentação académica e relatório em LaTeX
│   ├── capas/
│   │   └── capa.tex
│   ├── capitulos/
│   │   ├── 01_introducao.tex
│   │   ├── 02_desenvolvimento.tex
│   │   └── 03_conclusao.tex
│   ├── d43-main.pdf               # Relatório final compilado
│   └── d43-main.tex               # Ficheiro principal LaTeX
├── ref/                           # Documentação técnica do código gerada pelo Doxygen
│   ├── Doxyfile                   # Ficheiro de configuração do Doxygen
│   ├── html/                      # Documentação em formato HTML
│   └── latex/                     # Documentação em formato LaTeX
├── src/                           # Código-fonte da aplicação
│   ├── app.py                     # Aplicação web e dashboard reativo (Shiny)
│   └── parser.py                  # Módulo de leitura e processamento de ficheiros PS2
├── .gitignore                     # Configuração de ficheiros ignorados pelo Git
├── Makefile                       # Automação de tarefas (instalar, executar e limpar)
├── planeamento.md                 # Planeamento semanal e distribuição de tarefas
├── README.md                      # Documentação principal do repositório
└── requirements.txt               # Dependências Python do projeto
```

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python 3.10+** | Linguagem base do sistema |
| **Shiny for Python** | Framework reativa para construção da interface web |
| **Pandas** | Manipulação, limpeza e agregação de dados tabulares |
| **Plotly Express** | Criação de gráficos analíticos e interativos |
| **LaTeX / BibLaTeX** | Redação do relatório técnico e académico |
| **Doxygen** | Geração automática de documentação a partir dos docstrings do código |
| **Make** | Automação de tarefas de instalação e execução |

---

## 💻 Instalação e Execução

### Pré-requisitos
* Python 3.10 ou superior instalado.
* Gestor de pacotes `pip`.

### 1. Clonar o Repositório
```bash
git clone https://github.com/IPCALESI2526/d-43.git
cd d-43
```

### 2. Criar e Ativar Ambiente Virtual (Recomendado)
```bash
# No Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# No Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar as Dependências
Utilizando o `Makefile`:
```bash
make install
```
Ou diretamente via `pip`:
```bash
pip install -r requirements.txt
```

### 4. Iniciar a Aplicação
Utilizando o `Makefile`:
```bash
make run
```
Ou diretamente com o comando do Shiny:
```bash
shiny run src/app.py
```

Aceda à aplicação no seu navegador através do endereço local indicado (geralmente `http://127.0.0.1:8000`).

---

## 📄 Especificação do Formato PS2

Os ficheiros na pasta `data/` representam transmissões de débitos diretos organizados por registos posicionais:

| Tipo | Posição | Campo | Descrição |
| :---: | :---: | :--- | :--- |
| **1 (Cabeçalho)** | `01-09` | Data Interna | Data de criação do ficheiro (`AAAAMMDD`) |
| | `10-52` | Designação | Nome da entidade credora (ex: `IPCA Energy`) |
| | `53-62` | NIF Entidade | Número de identificação fiscal da entidade |
| | `63-75` | Valor Total | Montante acumulado do lote (em cêntimos) |
| | `76-81` | Quantidade | Número total de movimentos no lote |
| **2 (Movimento)** | `09-11` | ID Ordem | Sequencial do registo dentro do lote |
| | `12-20` | NIF Cliente | Primeiros 9 caracteres do campo de identificação |
| | `21-41` | NIB Cliente | Restantes 21 caracteres do campo de identificação |
| | `42-55` | Valor | Montante a debitar (em cêntimos) |
| | `56-82` | Descrição | Motivo do débito (ex: `Fatura Eletricidade 07/2025`) |
| **9 (Rodapé)** | `02-15` | Valor Total | Totalizador de verificação do lote (em cêntimos) |
| | `16-21` | Quantidade | Contagem final de registos para auditoria |

### Exemplo de Ficheiro (`DD_2025_07.ps2`)
```text
120250726IPCA Energy                                50123456700000000028779000010
2000000100100350651000025874125423568914200000000002136Fatura Eletricidade 07/2025
2000000100200330000452108745961550184592300000000004561Fatura Eletricidade 07/2025
2000000100300100000123456789012312345678900000000002063Fatura Eletricidade 07/2025
2000000100400360010234567890123429845123600000000002860Fatura Eletricidade 07/2025
2000000100500230099887766554433245678912300000000004507Fatura Eletricidade 07/2025
2000000100600380011223344556677887451236900000000002208Fatura Eletricidade 07/2025
2000000100700190055667788990011215975348600000000002208Fatura Eletricidade 07/2025
2000000100800420066554433221100995175325800000000002661Fatura Eletricidade 07/2025
2000000100900330012312312312312375315984200000000003077Fatura Eletricidade 07/2025
2000000101000110099880077665544362839415700000000002498Fatura Eletricidade 07/2025
900000000028779000010
```

---

## 📸 Demonstração

<div align="center">
  <img src="./assets/img/DashboardDebitos.png" alt="Interface do Dashboard de Débitos Diretos" width="95%">
  <p><em>Figura: Interface interativa desenvolvida com Shiny for Python com filtros de data, NIB e gráficos analíticos.</em></p>
</div>

---

## 👥 Equipa de Desenvolvimento (Grupo 43)

| Função no Planeamento | Número | Nome |
| :---: | :---: | :--- |
| **A1** | `29330` | Edgar Brito |
| **A2** | `29328` | Tiago Lima |
| **A3** | `29333` | Rui Araújo |
| **A4** | `29325` | Henrique Ribeiro |

Consulte o documento [planeamento.md](./planeamento.md) para detalhes semanais de branches, commits e distribuição de tarefas de cada elemento.

---

## 🔗 Referências

* [Documentação do Shiny for Python](https://shiny.posit.co/py/)
* [Guia de Utilizador do Pandas](https://pandas.pydata.org/docs/)
* [Documentação Interativa do Plotly](https://plotly.com/python/)
* [Manual Oficial do Doxygen](https://www.doxygen.nl/manual/)
* [Serviço gitignore.io](https://www.toptal.com/developers/gitignore)
