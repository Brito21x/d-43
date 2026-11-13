from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

try:
    from parser import processar_toda_pasta
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from parser import processar_toda_pasta

PASTA_SRC = Path(__file__).resolve().parent
PASTA_DATA = PASTA_SRC.parent / "data"

if PASTA_DATA.exists():
    df_global = processar_toda_pasta(str(PASTA_DATA))
    if not df_global.empty and 'data' in df_global.columns:
        df_global = df_global[df_global['data'].dt.year >= 2024]
else:
    df_global = pd.DataFrame()

def formatar_espacos(texto, n=4):
    if not isinstance(texto, str):
        return str(texto)
    return " ".join([texto[i:i+n] for i in range(0, len(texto), n)])

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Débitos Diretos"),
        ui.p("Gestão analítica de faturas e movimentos bancários PS2.", style="font-size: 0.85rem; color: #6c757d;"),
        ui.hr(),
        ui.input_date_range(
            "filtro_data", 
            "Período de Análise:",
            start=df_global['data'].min().date() if not df_global.empty else None,
            end=df_global['data'].max().date() if not df_global.empty else None
        ),
        ui.input_selectize(
            "filtro_clientes", 
            "Filtrar por Cliente (NIB):", 
            choices=list(df_global['cliente_nib'].unique()) if not df_global.empty else [], 
            multiple=True
        ),
        ui.input_action_button("btn_reset", "Limpar Filtros", class_="btn-outline-primary btn-sm w-100"),
        ui.hr(),
        ui.markdown("**IPCA Energy** • Laboratórios de Informática")
    ),
    ui.layout_columns(
        ui.value_box("Total Faturado", ui.output_text("kpi_valor"), theme="bg-gradient-blue-indigo"),
        ui.value_box("Total Movimentos", ui.output_text("kpi_qtd"), theme="text-primary"),
        ui.value_box("Valor Médio", ui.output_text("kpi_media"), theme="text-success"),
    ),
    ui.layout_columns(
        ui.card(ui.card_header("Evolução Temporal dos Débitos"), output_widget("grafico_linha")),
        ui.card(ui.card_header("Top 10 Clientes (Volume Acumulado)"), output_widget("grafico_barras")),
    ),
    ui.card(
        ui.card_header("Registo Detalhado de Movimentos"),
        ui.output_data_frame("tabela_dados")
    ),
    title="Dashboard de Débitos Diretos"
)

def server(input, output, session):

    @reactive.calc
    def dados_filtrados():
        if df_global.empty:
            return pd.DataFrame()
        df = df_global.copy()
        
        datas = input.filtro_data()
        if datas and datas[0] and datas[1]:
            df = df[(df['data'].dt.date >= datas[0]) & (df['data'].dt.date <= datas[1])]
        
        clientes = input.filtro_clientes()
        if clientes:
            df = df[df['cliente_nib'].isin(clientes)]
        return df

    @reactive.effect
    @reactive.event(input.btn_reset)
    def _():
        ui.update_date_range(
            "filtro_data",
            start=df_global['data'].min().date() if not df_global.empty else None,
            end=df_global['data'].max().date() if not df_global.empty else None
        )
        ui.update_selectize("filtro_clientes", selected=[])

    @render.text
    def kpi_valor():
        val = dados_filtrados()['valor'].sum() if not dados_filtrados().empty else 0.0
        return f"{val:,.2f} €"

    @render.text
    def kpi_qtd():
        return f"{len(dados_filtrados()):,} mov."

    @render.text
    def kpi_media():
        df = dados_filtrados()
        if df.empty or len(df) == 0:
            return "0.00 €"
        media = df['valor'].mean()
        return f"{media:,.2f} €"

    @render_widget
    def grafico_linha():
        df = dados_filtrados()
        if df.empty:
            return None
        
        df_tempo = df.groupby('data')['valor'].sum().reset_index().sort_values('data')
        df_tempo['data_txt'] = df_tempo['data'].dt.strftime('%Y-%m-%d')
        
        fig = px.line(
            df_tempo, 
            x='data_txt', 
            y='valor', 
            markers=True, 
            template="plotly_white",
            color_discrete_sequence=["#1f77b4"]
        )
        
        fig.update_xaxes(
            title_text="Data",
            type='date', 
            tickformat="%d/%m/%Y",
            tickangle=-45,
            automargin=True,
            showgrid=True,
            gridcolor="#f0f0f0"
        )
        fig.update_yaxes(
            title_text="Total (€)",
            rangemode="tozero",
            showgrid=True, 
            gridcolor="#f0f0f0"
        )
        fig.update_layout(
            hovermode="x unified"
        )
        fig.update_traces(
            hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Total:</b> %{y:.2f} €<extra></extra>",
            line=dict(width=2.5),
            marker=dict(size=7)
        )
        
        return fig

    @render_widget
    def grafico_barras():
        df = dados_filtrados()
        if df.empty:
            return None
        df_cli = df.groupby('cliente_nib')['valor'].sum().reset_index()
        df_cli = df_cli.sort_values(by='valor', ascending=False).head(10)
        
        df_cli['cliente_display'] = [f"Cliente {i+1} (...{str(nib)[-4:]})" for i, nib in enumerate(df_cli['cliente_nib'])]
        df_cli['nib_formatado'] = df_cli['cliente_nib'].apply(lambda x: formatar_espacos(x, 4))
        
        fig = px.bar(
            df_cli, 
            x='cliente_display', 
            y='valor', 
            template="plotly_white",
            color='valor',
            color_continuous_scale="Blues"
        )
        fig.update_layout(
            xaxis_title="Cliente", 
            yaxis_title="Total (€)", 
            coloraxis_showscale=False
        )
        fig.update_xaxes(
            tickangle=-30,
            automargin=True
        )
        fig.update_yaxes(
            rangemode="tozero",
            showgrid=True, 
            gridcolor="#f0f0f0"
        )
        fig.update_traces(
            customdata=df_cli['nib_formatado'],
            hovertemplate="<b>%{x}</b><br><b>NIB:</b> %{customdata}<br><b>Total Gasto:</b> %{y:.2f} €<extra></extra>"
        )
        return fig

    @render.data_frame
    def tabela_dados():
        df_view = dados_filtrados().copy()
        if not df_view.empty:
            df_view = df_view.sort_values(by='data', ascending=True)

            df_view['cliente_nib'] = df_view['cliente_nib'].apply(lambda x: formatar_espacos(x, 4))
            
            if 'cliente_nif' in df_view.columns:
                df_view['cliente_nif'] = df_view['cliente_nif'].apply(lambda x: formatar_espacos(x, 3))

            if 'entidade_nif' in df_view.columns:
                df_view['entidade_nif'] = df_view['entidade_nif'].apply(lambda x: formatar_espacos(x, 3))
                
            df_view['data'] = df_view['data'].dt.strftime('%d/%m/%Y')
            df_view['valor'] = df_view['valor'].apply(lambda x: f"{x:,.2f} €")
            
            colunas_ordem = ['data', 'entidade_nif', 'cliente_nif', 'cliente_nib', 'descricao', 'valor', 'ordem']
            cols_finais = [c for c in colunas_ordem if c in df_view.columns]
            df_view = df_view[cols_finais]

            df_view = df_view.rename(columns={
                'data': 'Data',
                'entidade_nif': 'NIF Entidade',
                'cliente_nif': 'NIF Cliente',
                'cliente_nib': 'NIB Cliente',
                'descricao': 'Descrição',
                'valor': 'Valor',
                'ordem': 'ID'
            })

        return render.DataGrid(df_view)

app = App(app_ui, server)
