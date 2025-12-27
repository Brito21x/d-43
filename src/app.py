from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

# Tenta importar o parser
try:
    from parser import processar_toda_pasta
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parser import processar_toda_pasta

# --- 1. Configuração e Leitura ---
PASTA_SRC = Path(__file__).parent
PASTA_DATA = PASTA_SRC.parent / "data"

print(f"--- A iniciar Dashboard ---")
print(f"A ler dados de: {PASTA_DATA}")

if PASTA_DATA.exists():
    df_global = processar_toda_pasta(str(PASTA_DATA))
    
    # Filtro de Segurança
    if not df_global.empty and 'data' in df_global.columns:
        df_global = df_global[df_global['data'].dt.year >= 2024]
        
    print(f"Sucesso: {len(df_global)} registos carregados.")
else:
    print("ERRO: Pasta 'data' não encontrada!")
    df_global = pd.DataFrame()

# --- Função Auxiliar ---
def formatar_espacos(texto, n=4):
    if not isinstance(texto, str): return str(texto)
    return " ".join([texto[i:i+n] for i in range(0, len(texto), n)])

# --- 2. Interface (UI) ---
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Dashboard Débitos"),
        ui.hr(),
        
        ui.input_date_range(
            "filtro_data", 
            "Selecionar Período:",
            start=df_global['data'].min().date() if not df_global.empty else None,
            end=df_global['data'].max().date() if not df_global.empty else None
        ),
        
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
        ui.value_box("Total Gasto", ui.output_text("kpi_valor"), theme="bg-gradient-blue-indigo"),
        ui.value_box("Nº Movimentos", ui.output_text("kpi_qtd"), theme="text-primary"),
    ),
    ui.layout_columns(
        ui.card(ui.card_header("Evolução Temporal"), output_widget("grafico_linha")),
        ui.card(ui.card_header("Top Clientes (Gastos)"), output_widget("grafico_barras")),
    ),
    ui.card(
        ui.card_header("Dados Detalhados"),
        ui.output_data_frame("tabela_dados")
    )
)

# --- 3. Servidor ---
def server(input, output, session):

    @reactive.calc
    def dados_filtrados():
        if df_global.empty: return pd.DataFrame()
        df = df_global.copy()
        
        datas = input.filtro_data()
        if datas and datas[0] and datas[1]:
            df = df[(df['data'].dt.date >= datas[0]) & (df['data'].dt.date <= datas[1])]
        
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
        
        df_tempo = df.groupby('data')['valor'].sum().reset_index().sort_values('data')
        
        # Converter para texto para o gráfico
        df_tempo['data_txt'] = df_tempo['data'].dt.strftime('%Y-%m-%d')
        
        fig = px.line(df_tempo, x='data_txt', y='valor', markers=True, template="plotly_white")
        
        fig.update_xaxes(
            title_text="Data",
            type='date', 
            tickformat="%d/%m/%Y",
            tickangle=-45
        )
        fig.update_layout(yaxis_title="Total (€)", hovermode="x unified")
        fig.update_traces(hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Total:</b> %{y:.2f} €<extra></extra>")
        
        return fig

    @render_widget
    def grafico_barras():
        df = dados_filtrados()
        if df.empty: return None
        df_cli = df.groupby('cliente_nib')['valor'].sum().reset_index()
        df_cli = df_cli.sort_values(by='valor', ascending=False).head(10)
        
        fig = px.bar(df_cli, x='cliente_nib', y='valor', template="plotly_white")
        fig.update_layout(xaxis_title="Cliente (NIB)", yaxis_title="Total (€)", xaxis_tickangle=-45)
        return fig

    @render.data_frame
    def tabela_dados():
        df_view = dados_filtrados().copy()
        if not df_view.empty:
            
            # --- 1. ORDENAR POR DATA (A Correção é Aqui) ---
            # ascending=True mete do mais antigo para o mais recente
            # ascending=False mete do mais recente para o mais antigo
            df_view = df_view.sort_values(by='data', ascending=True)

            # --- 2. Formatações Visuais ---
            df_view['cliente_nib'] = df_view['cliente_nib'].apply(lambda x: formatar_espacos(x, 4))
            
            if 'cliente_nif' in df_view.columns:
                df_view['cliente_nif'] = df_view['cliente_nif'].apply(lambda x: formatar_espacos(x, 3))

            if 'entidade_nif' in df_view.columns:
                df_view['entidade_nif'] = df_view['entidade_nif'].apply(lambda x: formatar_espacos(x, 3))
                
            df_view['data'] = df_view['data'].dt.strftime('%d/%m/%Y')
            
            # --- 3. Selecionar e Traduzir Colunas ---
            colunas_ordem = ['data', 'entidade_nif', 'cliente_nif', 'cliente_nib', 'descricao', 'valor', 'ordem']
            cols_finais = [c for c in colunas_ordem if c in df_view.columns]
            df_view = df_view[cols_finais]

            df_view = df_view.rename(columns={
                'data': 'Data',
                'entidade_nif': 'NIF Entidade',
                'cliente_nif': 'NIF Cliente',
                'cliente_nib': 'NIB Cliente',
                'descricao': 'Descrição',
                'valor': 'Valor (€)',
                'ordem': 'ID'
            })

        return render.DataGrid(df_view)

app = App(app_ui, server)
