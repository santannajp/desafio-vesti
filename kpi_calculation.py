import pandas as pd
import json

# Definindo o caminho do arquivo final
INPUT_FILE = "upload/final_dataset.csv"
OUTPUT_FILE = "upload/kpis.json"
METADATA_FILE = "upload/metadata.json"

def calculate_kpis():
    """Calcula os principais indicadores de negócio (KPIs) para o dashboard."""
    print("Iniciando o cálculo dos KPIs...")
    
    # Carregar o dataset final
    df = pd.read_csv(INPUT_FILE)
    df['order_date'] = pd.to_datetime(df['order_date'], format='mixed', utc=True).dt.tz_convert(None)
    
    # Carregar metadados para obter o período de análise
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    
    # --- KPIs Globais ---
    
    # 1. Receita Total (Total Revenue)
    total_revenue = df['total_value'].sum()
    
    # 2. Número Total de Pedidos (Total Orders)
    total_orders = df['order_id'].nunique()
    
    # 3. Ticket Médio (Average Ticket)
    average_ticket = total_revenue / total_orders if total_orders > 0 else 0
    
    # 4. Número Total de Clientes (Total Customers - usando documento como identificador)
    total_customers = df['customer_document'].nunique()
    
    # 5. Taxa de Aquisição de Novos Clientes (New Customer Acquisition Rate)
    # Clientes que fizeram a primeira compra no período de análise
    new_customers = df[df['is_first_purchase'] == True]['customer_document'].nunique()
    
    # 6. Receita por Canal de Venda (Revenue by Channel)
    revenue_by_channel = df.groupby('sales_channel')['total_value'].sum().to_dict()
    
    # 7. Pedidos por Canal de Venda (Orders by Channel)
    orders_by_channel = df.groupby('sales_channel')['order_id'].nunique().to_dict()
    
    # 8. Vendas por Vendedor (Sales by Seller - para Gerente de Loja/Vendedor)
    sales_by_seller = df.groupby('seller_name')['total_value'].sum().sort_values(ascending=False).head(10).to_dict()
    
    # 9. Distribuição de Pedidos por Dia da Semana (Orders by Weekday)
    # Traduzir o nome do dia da semana para português
    weekday_map = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    df['order_weekday_pt'] = df['order_weekday'].map(weekday_map)
    orders_by_weekday = df.groupby('order_weekday_pt')['order_id'].nunique().to_dict()
    
    # 10. Clientes Ativos vs Inativos (CRM)
    customer_status_count = df.drop_duplicates(subset=['customer_document'])['customer_status'].value_counts().to_dict()
    
    # --- KPIs de Tendência (Time Series) ---
    
    # 11. Receita Mensal (Monthly Revenue)
    monthly_revenue = df.set_index('order_date').resample('M')['total_value'].sum().to_dict()
    
    # 12. Pedidos Mensais (Monthly Orders)
    monthly_orders = df.set_index('order_date').resample('M')['order_id'].nunique().to_dict()
    
    # --- Estrutura de Dados para o Dashboard ---
    
    kpis = {
        "period_start": metadata.get("min_order_date"),
        "period_end": metadata.get("max_order_date"),
        "global_kpis": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "average_ticket": average_ticket,
            "total_customers": total_customers,
            "new_customers": new_customers,
        },
        "channel_kpis": {
            "revenue_by_channel": revenue_by_channel,
            "orders_by_channel": orders_by_channel,
        },
        "seller_kpis": {
            "sales_by_seller": sales_by_seller,
        },
        "customer_kpis": {
            "customer_status_count": customer_status_count,
        },
        "time_kpis": {
            "orders_by_weekday": orders_by_weekday,
            "monthly_revenue": {str(k): v for k, v in monthly_revenue.items()}, # Converter Timestamp para string
            "monthly_orders": {str(k): v for k, v in monthly_orders.items()}, # Converter Timestamp para string
        }
    }
    
    # Salvar os KPIs em um arquivo JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(kpis, f, indent=4)
        
    print(f"KPIs calculados e salvos em: {OUTPUT_FILE}")

if __name__ == "__main__":
    calculate_kpis()
