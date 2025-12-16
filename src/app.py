from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

# Garante que conseguimos importar o parser que está na mesma pasta
try:
    from parser import processar_toda_pasta
except ImportError:
    # Caso estejas a correr de uma forma diferente, tenta adicionar o caminho
    sys.path.append(str(Path(__file__).parent))
    from parser import processar_toda_pasta

# --- 1. Configuração e Leitura de Dados ---
PASTA_SRC = Path(__file__).parent
PASTA_DATA = PASTA_SRC.parent / "data"

print(f"--- A iniciar Dashboard ---")
print(f"A ler dados de: {PASTA_DATA}")

if PASTA_DATA.exists():
    df_global = processar_toda_pasta(str(PASTA_DATA))
    print(f"Sucesso: {len(df_global)} registos carregados.")
else:
    print("ERRO: Pasta 'data' não encontrada!")
    df_global = pd.DataFrame()

# --- 2. Interface Gráfica (UI) ---
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Dashboard Débitos"),
        ui.hr(),
        
        # Filtro Data
        ui.input_date_range(
            "filtro_data", 
            "Selecionar Período:",
            start=df_global['data'].min().date() if not df_global.empty else None,
            end=df_global['data'].max().date() if not df_global.empty else None
        ),
        
        # Filtro Clientes
        # CORREÇÃO: Removemos o argumento 'placeholder' que estava a dar erro
        ui.input_selectize(
            "filtro_clientes", 
            "Filtrar Clientes (NIB):", 
            choices=list(df_global['cliente_nib'].unique()) if not df_global.empty else [], 
            multiple=True
        ),
        ui.hr(),
        ui.markdown("Trabalho Prático **LI 2025**")
    ),
    
    ui.layout_columns(
        ui.value_box(
            "Total Gasto", 
            ui.output_text("kpi_valor"), 
            theme="bg-gradient-blue-indigo"
        ),
        ui.value_box(
            "Nº Movimentos", 
            ui.output_text("kpi_qtd"), 
            theme="text-primary"
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Evolução Temporal"),
            output_widget("grafico_linha")
        ),
        ui.card(
            ui.card_header("Top Clientes (Gastos)"),
            output_widget("grafico_barras")
        ),
    ),
    ui.card(
        ui.card_header("Dados Detalhados"),
        ui.output_data_frame("tabela_dados")
    )
)

# --- 3. Lógica do Servidor (Server) ---
def server(input, output, session):

    @reactive.calc
    def dados_filtrados():
        if df_global.empty: return pd.DataFrame()
        
        df = df_global.copy()
        
        # Filtro Data
        datas = input.filtro_data()
        if datas and datas[0] and datas[1]:
            df = df[(df['data'].dt.date >= datas[0]) & (df['data'].dt.date <= datas[1])]
        
        # Filtro Clientes
        clientes = input.filtro_clientes()
        if clientes:
            df = df[df['cliente_nib'].isin(clientes)]
            
        return df

    @render.text
    def kpi_valor():
        val = dados_filtrados()['valor'].sum() if not dados_filtrados().empty else 0.0
        return f"{val:,.2f} €"

    @render.text
    def kpi_qtd():
        return str(len(dados_filtrados()))

    @render_widget
    def grafico_linha():
        df = dados_filtrados()
        if df.empty: return None
        # Agrupar por dia
        df_dia = df.groupby('data')['valor'].sum().reset_index()
        return px.line(df_dia, x='data', y='valor', markers=True, template="plotly_white")

    @render_widget
    def grafico_barras():
        df = dados_filtrados()
        if df.empty: return None
        # Agrupar por cliente
        df_cli = df.groupby('cliente_nib')['valor'].sum().reset_index()
        df_cli = df_cli.sort_values(by='valor', ascending=False).head(10)
        return px.bar(df_cli, x='cliente_nib', y='valor', template="plotly_white")

    @render.data_frame
    def tabela_dados():
        return render.DataGrid(dados_filtrados())

app = App(app_ui, server)
