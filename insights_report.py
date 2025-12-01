import pandas as pd
import json
from datetime import datetime

# Definindo os caminhos dos arquivos
DATA_FILE = "/home/ubuntu/final_dataset.csv"
KPI_FILE = "/home/ubuntu/kpis.json"
OUTPUT_FILE = "/home/ubuntu/relatorio_insights.md"

def generate_insights_report():
    """Gera um relatório de insights e análises estratégicas."""
    print("Iniciando a geração do relatório de insights...")
    
    # Carregar dados e KPIs
    df = pd.read_csv(DATA_FILE)
    df['order_date'] = pd.to_datetime(df['order_date'], format='mixed', utc=True).dt.tz_convert(None)
    
    with open(KPI_FILE, 'r', encoding='utf-8') as f:
        kpis = json.load(f)
        
    # --- Dados para Análise ---
    
    total_revenue = kpis['global_kpis']['total_revenue']
    total_orders = kpis['global_kpis']['total_orders']
    average_ticket = kpis['global_kpis']['average_ticket']
    new_customers = kpis['global_kpis']['new_customers']
    
    revenue_by_channel = kpis['channel_kpis']['revenue_by_channel']
    orders_by_channel = kpis['channel_kpis']['orders_by_channel']
    
    sales_by_seller = kpis['seller_kpis']['sales_by_seller']
    
    customer_status_count = kpis['customer_kpis']['customer_status_count']
    
    # --- Análise de Sustentação e Escalabilidade ---
    
    sustentacao_escalabilidade = """
    ## 4. Sustentação e 5. Escalabilidade da Solução
    
    A solução proposta, baseada em **Python** com as bibliotecas **Pandas** para processamento de dados e **Plotly/Dash** para visualização, atende aos requisitos de sustentação e escalabilidade.
    
    | Requisito | Solução Proposta | Vantagens |
    | :--- | :--- | :--- |
    | **Sustentação** (Manutenção de Dados) | Scripts de ETL (Extração, Transformação e Carga) em Python. | A lógica de limpeza e integração está centralizada nos scripts `data_integration.py` e `data_modeling.py`. Isso permite a **automação** do processo via *cron jobs* ou ferramentas de orquestração (como Apache Airflow), garantindo que o dashboard seja atualizado com novos dados de forma regular e confiável. |
    | **Escalabilidade** (Adição de Indicadores) | Modelo de dados unificado e modular. | O *dataset* final (`final_dataset.csv`) é a única fonte de verdade. Novos indicadores podem ser facilmente adicionados ao script `kpi_calculation.py` ou diretamente no Dash, sem a necessidade de reestruturar a base de dados. A arquitetura em camadas (Dados Brutos -> Dados Integrados -> KPIs -> Dashboard) facilita a manutenção e a expansão. |
    """
    
    # --- Análise de Indicadores e Insights ---
    
    # 1. Análise de Canais
    total_revenue_channel = sum(revenue_by_channel.values())
    
    channel_analysis = f"""
    ## 3. Indicadores e Insights Chave
    
    ### 3.1. Performance por Canal de Venda
    
    A análise da performance por canal é fundamental para o **CEO** e o **Marketing**.
    
    | Canal | Receita (R$) | Pedidos | Ticket Médio (R$) | % da Receita |
    | :--- | :--- | :--- | :--- | :--- |
    | Físico (ERP) | R$ {revenue_by_channel.get('Físico', 0):,.2f} | {orders_by_channel.get('Físico', 0):,} | {revenue_by_channel.get('Físico', 0) / orders_by_channel.get('Físico', 1):,.2f} | {revenue_by_channel.get('Físico', 0) / total_revenue_channel * 100:.1f}% |
    | Online (E-commerce) | R$ {revenue_by_channel.get('Online', 0):,.2f} | {orders_by_channel.get('Online', 0):,} | {revenue_by_channel.get('Online', 0) / orders_by_channel.get('Online', 1):,.2f} | {revenue_by_channel.get('Online', 0) / total_revenue_channel * 100:.1f}% |
    
    **Insight:** O canal **Físico** (ERP) é o principal motor de receita e volume de pedidos. No entanto, o **Ticket Médio** do canal Online é significativamente maior (R$ {revenue_by_channel.get('Online', 0) / orders_by_channel.get('Online', 1):,.2f} vs R$ {revenue_by_channel.get('Físico', 0) / orders_by_channel.get('Físico', 1):,.2f}).
    
    **Ação Sugerida:** O Marketing deve investigar os fatores que elevam o Ticket Médio Online (ex: promoções, mix de produtos, frete grátis) e tentar replicar essas estratégias no ambiente físico, ou vice-versa, se o mix de produtos for diferente.
    """
    
    # 2. Análise de Clientes (Marketing)
    
    total_customers = kpis['global_kpis']['total_customers']
    active_customers = customer_status_count.get('active', 0)
    inactive_customers = customer_status_count.get('inactive', 0)
    
    customer_analysis = f"""
    ### 3.2. Aquisição e Status de Clientes (CRM)
    
    O **Marketing** e o **CEO** se beneficiam da visão de clientes.
    
    - **Novos Clientes Adquiridos:** {new_customers:,}
    - **Total de Clientes na Base (Documentos Únicos):** {total_customers:,}
    
    | Status (CRM) | Contagem | % da Base |
    | :--- | :--- | :--- |
    | Ativo | {active_customers:,} | {active_customers / total_customers * 100:.1f}% |
    | Inativo | {inactive_customers:,} | {inactive_customers / total_customers * 100:.1f}% |
    | Desconhecido | {customer_status_count.get('Desconhecido', 0):,} | {customer_status_count.get('Desconhecido', 0) / total_customers * 100:.1f}% |
    
    **Insight:** A base de clientes possui uma alta taxa de clientes **Inativos** ({inactive_customers:,}). Além disso, há um número significativo de clientes com status **Desconhecido**, indicando que o processo de integração CRM/Vendas pode ter falhas ou que há clientes que compraram mas não foram devidamente classificados.
    
    **Ação Sugerida:** O Marketing deve criar campanhas de **reativação** focadas nos clientes inativos. A TI deve investigar a origem dos clientes com status "Desconhecido" para garantir a integridade dos dados.
    """
    
    # 3. Análise de Vendedores (Gerente de Loja / Vendedor)
    
    seller_analysis = f"""
    ### 3.3. Performance de Vendas por Vendedor
    
    Esses indicadores são cruciais para o **Gerente de Loja** e para o **Vendedor** individual.
    
    **Top 5 Vendedores por Receita:**
    
    | Posição | Vendedor | Receita (R$) |
    | :--- | :--- | :--- |
    """
    
    # Ordenar e limitar a 5
    sorted_sellers = sorted(sales_by_seller.items(), key=lambda item: item[1], reverse=True)
    
    for i, (seller, sales) in enumerate(sorted_sellers[:5]):
        seller_analysis += f"| {i+1} | {seller} | R$ {sales:,.2f} |\n"
        
    seller_analysis += f"""
    **Insight:** O dashboard permite ao Gerente de Loja identificar rapidamente os vendedores de alta performance e aqueles que podem precisar de treinamento ou suporte.
    
    **Ação Sugerida:** O Gerente de Loja deve analisar as estratégias dos Top Vendedores (ex: **{sorted_sellers[0][0]}** e **{sorted_sellers[1][0]}**) e implementar um programa de *mentoring* ou compartilhamento de melhores práticas para o restante da equipe.
    """
    
    # --- Estrutura do Relatório ---
    
    report_content = f"""# Relatório de Análise e Insights - Dashboard de Performance da Confecção

**Data de Geração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Período de Análise:** {kpis.get('period_start', 'N/A')} a {kpis.get('period_end', 'N/A')}

## 1. Resumo Executivo (CEO)

O dashboard consolidado oferece uma visão 360º do negócio, integrando dados de vendas (ERP e E-commerce) e clientes (CRM).

| Métrica Chave | Valor |
| :--- | :--- |
| **Receita Total** | R$ {total_revenue:,.2f} |
| **Total de Pedidos** | {total_orders:,} |
| **Ticket Médio** | R$ {average_ticket:,.2f} |
| **Novos Clientes** | {new_customers:,} |

## 2. Plataforma e Modelagem (O que será avaliado: 1)

A plataforma escolhida é o **Plotly Dash**, uma biblioteca Python ideal para prototipagem rápida de dashboards interativos e que se alinha ao requisito de ser feito em Python.

### 2.1. Modelagem de Dados

A modelagem adotada segue o princípio de **Star Schema** simplificado, onde a tabela de **Fatos** (Pedidos) é unificada e enriquecida com atributos de **Dimensão** (Clientes e Tempo).

- **Integração:** Os dados de ERP (Físico) e E-commerce (Online) foram unificados em uma única tabela de pedidos, utilizando o campo `customer_document` (CPF/CNPJ) como chave para enriquecimento com dados do CRM.
- **Limpeza:** Foi aplicada limpeza e padronização no campo de documento e nos nomes dos vendedores, garantindo a integridade da análise.
- **Enriquecimento:** Criação de colunas de tempo (`order_year`, `order_month`, etc.) e de categoria (`sales_channel`, `is_first_purchase`) para análises mais granulares.

{channel_analysis}

{customer_analysis}

{seller_analysis}

{sustentacao_escalabilidade}

## 6. Personalização (O que será avaliado: 6)

O dashboard foi estruturado com **abas dedicadas** para cada *persona*, garantindo que cada usuário tenha acesso imediato aos indicadores mais relevantes para sua função:

| Persona | Indicadores Chave | Foco Estratégico |
| :--- | :--- | :--- |
| **CEO** | Receita Total, Ticket Médio, Evolução Mensal, Distribuição por Canal. | Visão macro, saúde financeira e crescimento. |
| **Marketing** | Novos Clientes, Status da Base (Ativo/Inativo), Performance por Canal. | Aquisição, retenção e eficácia das campanhas. |
| **Gerente de Loja** | Vendas por Vendedor, Performance do Canal Físico. | Gestão de equipe e otimização da loja física. |
| **Vendedor** | Performance Individual (Receita, Pedidos, Ticket Médio). | Acompanhamento de metas e autoavaliação. |

O código do dashboard (em `dashboard_generator.py`) e o HTML estático (em `dashboard.html`) serão fornecidos como entrega final.
"""
    
    # Salvar o relatório
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Relatório de insights salvo em: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_insights_report()
