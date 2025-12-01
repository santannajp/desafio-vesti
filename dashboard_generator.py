import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Definindo os caminhos dos arquivos
DATA_FILE = "upload/final_dataset.csv"
KPI_FILE = "upload/kpis.json"
OUTPUT_HTML = "upload/dashboard.html"

# Escolhendo um tema Bootstrap para um visual moderno e limpo
# Inspirado nos exemplos, vamos usar o tema FLATLY ou CERULEAN
THEME = dbc.themes.FLATLY

# --- Funções de Carregamento de Dados ---

def load_data():
    """Carrega o dataset final e os KPIs."""
    df = pd.read_csv(DATA_FILE)
    df['order_date'] = pd.to_datetime(df['order_date'], format='mixed', utc=True).dt.tz_convert(None)
    
    with open(KPI_FILE, 'r', encoding='utf-8') as f:
        kpis = json.load(f)
        
    return df, kpis

# --- Funções de Visualização ---

def create_kpi_card(title, value, format_str="R$ {:,.2f}", icon="cash-stack"):
    """Cria um componente dbc.Card para um cartão de KPI."""
    if isinstance(value, (int, float)):
        display_value = format_str.format(value).replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        display_value = str(value)
        
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-subtitle text-muted"),
            html.H4(display_value, className="card-title text-primary"),
            html.I(className=f"bi bi-{icon} me-2", style={"fontSize": "2rem", "color": "#007bff"})
        ], className="d-flex justify-content-between align-items-center"),
        className="shadow-sm h-100"
    )

def create_revenue_by_channel_chart(kpis):
    """Cria o gráfico de Receita por Canal."""
    df_channel = pd.DataFrame(list(kpis['channel_kpis']['revenue_by_channel'].items()), columns=['Canal', 'Receita'])
    fig = px.bar(df_channel, x='Canal', y='Receita', title='Receita por Canal de Venda',
                 color='Canal', text='Receita',
                 labels={'Receita': 'Receita (R$)'},
                 height=400)
    fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title=None, title_x=0.5)
    return dcc.Graph(figure=fig)

def create_monthly_revenue_chart(kpis):
    """Cria o gráfico de Evolução da Receita Mensal."""
    df_monthly = pd.DataFrame(list(kpis['time_kpis']['monthly_revenue'].items()), columns=['Mês', 'Receita'])
    df_monthly['Mês'] = pd.to_datetime(df_monthly['Mês']).dt.to_period('M').astype(str)
    
    fig = px.line(df_monthly, x='Mês', y='Receita', title='Evolução da Receita Mensal',
                  labels={'Receita': 'Receita (R$)'},
                  markers=True, height=400)
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5)
    return dcc.Graph(figure=fig)

def create_sales_by_seller_chart(kpis):
    """Cria o gráfico de Vendas por Vendedor (Top 10)."""
    df_seller = pd.DataFrame(list(kpis['seller_kpis']['sales_by_seller'].items()), columns=['Vendedor', 'Vendas'])
    fig = px.bar(df_seller.head(10), x='Vendas', y='Vendedor', orientation='h',
                 title='Top 10 Vendedores por Receita',
                 labels={'Vendas': 'Receita (R$)'},
                 text='Vendas',
                 height=450)
    fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, title_x=0.5)
    return dcc.Graph(figure=fig)

def create_customer_status_chart(kpis):
    """Cria o gráfico de Status do Cliente (Ativo/Inativo)."""
    df_status = pd.DataFrame(list(kpis['customer_kpis']['customer_status_count'].items()), columns=['Status', 'Contagem'])
    fig = px.pie(df_status, values='Contagem', names='Status', title='Status dos Clientes (CRM)',
                 hole=.3, height=400)
    fig.update_traces(textinfo='percent+label', pull=[0.1 if s == 'active' else 0 for s in df_status['Status']])
    fig.update_layout(title_x=0.5)
    return dcc.Graph(figure=fig)

# --- Layout do Dashboard ---

def create_dashboard_layout(kpis, df):
    """Define o layout do dashboard com base nas personas, usando DBC."""
    
    # KPIs Globais
    kpi_cards = dbc.Row([
        dbc.Col(create_kpi_card("Receita Total", kpis['global_kpis']['total_revenue'], icon="currency-dollar"), md=2),
        dbc.Col(create_kpi_card("Total de Pedidos", kpis['global_kpis']['total_orders'], format_str="{:,.0f}", icon="bag"), md=2),
        dbc.Col(create_kpi_card("Ticket Médio", kpis['global_kpis']['average_ticket'], icon="ticket"), md=2),
        dbc.Col(create_kpi_card("Total de Clientes", kpis['global_kpis']['total_customers'], format_str="{:,.0f}", icon="people"), md=3),
        dbc.Col(create_kpi_card("Novos Clientes", kpis['global_kpis']['new_customers'], format_str="{:,.0f}", icon="person-plus"), md=3),
    ], className="mb-4")
    
    # Conteúdo para cada aba (Persona)
    
    # 1. CEO
    ceo_content = dbc.Container(fluid=True, children=[
        kpi_cards,
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=create_monthly_revenue_chart(kpis).figure), className="shadow-sm h-100"), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=create_revenue_by_channel_chart(kpis).figure), className="shadow-sm h-100"), md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=create_customer_status_chart(kpis).figure), className="shadow-sm h-100"), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=create_sales_by_seller_chart(kpis).figure), className="shadow-sm h-100"), md=6),
        ], className="mb-4"),
    ])
    
    # 2. Marketing
    marketing_content = dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col(create_kpi_card("Novos Clientes Adquiridos", kpis['global_kpis']['new_customers'], format_str="{:,.0f}", icon="person-plus"), md=4),
            dbc.Col(create_kpi_card("Receita Online", kpis['channel_kpis']['revenue_by_channel'].get('Online', 0), icon="globe"), md=4),
            dbc.Col(create_kpi_card("Pedidos Online", kpis['channel_kpis']['orders_by_channel'].get('Online', 0), format_str="{:,.0f}", icon="cart"), md=4),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=create_customer_status_chart(kpis).figure), className="shadow-sm h-100"), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=create_revenue_by_channel_chart(kpis).figure), className="shadow-sm h-100"), md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=px.bar(pd.DataFrame(list(kpis['time_kpis']['orders_by_weekday'].items()), columns=['Dia', 'Pedidos']), 
                                x='Dia', y='Pedidos', title='Pedidos por Dia da Semana', height=400).update_layout(title_x=0.5)), className="shadow-sm h-100"), md=12),
        ], className="mb-4"),
    ])
    
    # 3. Gerente de Loja
    loja_content = dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col(create_kpi_card("Receita Total (Físico)", kpis['channel_kpis']['revenue_by_channel'].get('Físico', 0), icon="shop"), md=4),
            dbc.Col(create_kpi_card("Total de Pedidos (Físico)", kpis['channel_kpis']['orders_by_channel'].get('Físico', 0), format_str="{:,.0f}", icon="bag-fill"), md=4),
            dbc.Col(create_kpi_card("Ticket Médio (Físico)", kpis['channel_kpis']['revenue_by_channel'].get('Físico', 0) / kpis['channel_kpis']['orders_by_channel'].get('Físico', 1), icon="ticket-fill"), md=4),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=create_sales_by_seller_chart(kpis).figure), className="shadow-sm h-100"), md=12),
        ], className="mb-4"),
    ])
    
    # 4. Vendedor
    vendedor_content = dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col(html.H5("Selecione o Vendedor:"), md=3),
            dbc.Col(dcc.Dropdown(
                id='seller-dropdown',
                options=[{'label': k, 'value': k} for k in kpis['seller_kpis']['sales_by_seller'].keys()],
                value=list(kpis['seller_kpis']['sales_by_seller'].keys())[0] if kpis['seller_kpis']['sales_by_seller'] else None,
                className="mb-3"
            ), md=9),
        ], className="mb-4"),
        html.Div(id='seller-output-container'),
    ])
    
    # Layout principal
    layout = dbc.Container(fluid=True, children=[
        dbc.Row(dbc.Col(html.H1("Dashboard de Performance da Confecção", className="text-center my-4 text-primary"))),
        dbc.Tabs(id="tabs-persona", active_tab='tab-ceo', children=[
            dbc.Tab(label='CEO', tab_id='tab-ceo', children=ceo_content),
            dbc.Tab(label='Marketing', tab_id='tab-marketing', children=marketing_content),
            dbc.Tab(label='Gerente de Loja', tab_id='tab-loja', children=loja_content),
            dbc.Tab(label='Vendedor', tab_id='tab-vendedor', children=vendedor_content),
        ], className="mb-4"),
    ])
    
    return layout

# --- Aplicação Dash ---

def run_dashboard_generator():
    """Inicializa e executa o gerador de dashboard."""
    
    # Certifique-se de que o DBC está instalado e o tema é carregado
    app = Dash(__name__, external_stylesheets=[THEME, dbc.icons.BOOTSTRAP])
    
    df, kpis = load_data()
    app.layout = create_dashboard_layout(kpis, df)
    
    # Callback para a aba do Vendedor
    @app.callback(
        Output('seller-output-container', 'children'),
        [Input('seller-dropdown', 'value')]
    )
    def update_seller_output(selected_seller):
        if not selected_seller:
            return dbc.Alert("Selecione um vendedor para ver os detalhes.", color="info")
        
        df_seller = df[df['seller_name'] == selected_seller]
        
        if df_seller.empty:
            return dbc.Alert(f"Nenhum dado encontrado para o vendedor {selected_seller}.", color="warning")
            
        total_sales = df_seller['total_value'].sum()
        total_orders = df_seller['order_id'].nunique()
        avg_ticket = total_sales / total_orders if total_orders > 0 else 0
        
        # Vendas por canal do vendedor
        sales_by_channel = df_seller.groupby('sales_channel')['total_value'].sum().reset_index()
        fig_channel = px.pie(sales_by_channel, values='total_value', names='sales_channel', 
                             title=f'Distribuição de Vendas por Canal para {selected_seller}',
                             hole=.3, height=350)
        fig_channel.update_layout(title_x=0.5)
        
        # Vendas por mês do vendedor
        df_monthly_seller = df_seller.set_index('order_date').resample('M')['total_value'].sum().reset_index()
        df_monthly_seller['order_date'] = df_monthly_seller['order_date'].dt.to_period('M').astype(str)
        fig_monthly = px.line(df_monthly_seller, x='order_date', y='total_value', 
                              title=f'Evolução Mensal de Vendas para {selected_seller}',
                              labels={'total_value': 'Receita (R$)', 'order_date': 'Mês'},
                              markers=True, height=350)
        fig_monthly.update_layout(xaxis_tickangle=-45, title_x=0.5)
        
        return dbc.Container(fluid=True, children=[
            dbc.Row([
                dbc.Col(create_kpi_card(f"Receita de {selected_seller}", total_sales, icon="cash"), md=4),
                dbc.Col(create_kpi_card(f"Pedidos de {selected_seller}", total_orders, format_str="{:,.0f}", icon="bag-check"), md=4),
                dbc.Col(create_kpi_card(f"Ticket Médio de {selected_seller}", avg_ticket, icon="ticket-detailed"), md=4),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_channel), className="shadow-sm h-100"), md=6),
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_monthly), className="shadow-sm h-100"), md=6),
            ], className="mb-4"),
        ])

    # --- Geração do HTML Estático (Apenas para visualização) ---
    # A geração de HTML estático é complexa com DBC, mas vamos simplificar para a entrega.
    # O foco é o servidor interativo.
    
    # Inicia o servidor Dash para a versão interativa
    print("\nIniciando o servidor Dash interativo aprimorado...")
    app.run(debug=True)

if __name__ == "__main__":
    run_dashboard_generator()