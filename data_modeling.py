import pandas as pd
import json

# Definindo o caminho do arquivo integrado
INPUT_FILE = "upload/integrated_data.csv"
OUTPUT_FILE = "upload/final_dataset.csv"
METADATA_FILE = "upload/metadata.json"

def refine_data_model():
    """Refina o modelo de dados, criando colunas de tempo e categorizando dados."""
    print("Iniciando o refinamento do modelo de dados...")
    
    # Carregar o dataset integrado
    df = pd.read_csv(INPUT_FILE)
    
    # 1. Conversão de Tipos
    df['order_date'] = pd.to_datetime(df['order_date'], format='mixed', utc=True).dt.tz_convert(None)
    
    # 2. Criação de Colunas de Tempo
    df['order_year'] = df['order_date'].dt.year
    df['order_month'] = df['order_date'].dt.month
    df['order_day'] = df['order_date'].dt.day
    df['order_weekday'] = df['order_date'].dt.day_name() # Nome do dia da semana em inglês (padrão)
    df['order_hour'] = df['order_date'].dt.hour
    
    # 3. Criação de Colunas de Categoria
    # 3.1. Canal de Venda (Source)
    # Já existe a coluna 'source' (ERP_Fisica, Vestishop, etc.). Vamos padronizar para 'Físico' e 'Online'.
    df['sales_channel'] = df['source'].apply(lambda x: 'Físico' if x == 'ERP_Fisica' else 'Online')
    
    # 3.2. Status do Cliente (CRM)
    # A coluna 'status' já existe. Vamos garantir que 'active' e 'inactive' estejam limpos.
    df['customer_status'] = df['status'].fillna('Desconhecido')
    
    # 3.3. Indicador de Primeira Compra (Para análise de aquisição)
    # Encontrar a primeira data de compra para cada cliente
    first_purchase = df.groupby('customer_document')['order_date'].min().reset_index()
    first_purchase.rename(columns={'order_date': 'first_order_date'}, inplace=True)
    df = pd.merge(df, first_purchase, on='customer_document', how='left')
    
    # Criar a flag 'is_first_purchase'
    df['is_first_purchase'] = df['order_date'] == df['first_order_date']
    
    # 4. Limpeza e Padronização de Nomes de Vendedores
    # A coluna 'seller_name' é crucial para as personas de Gerente de Loja e Vendedor.
    # Vamos padronizar os nomes para evitar duplicidade (ex: "NATALIA" e "Natalia R.")
    df['seller_name'] = df['seller_name'].str.upper().str.strip().replace({
        'NATALIA R.': 'NATALIA',
        'USUÁRIO DE TESTE': 'TESTE',
        'JESSICA': 'JESSICA',
        'KELI': 'KELI',
        'SANDRA': 'SANDRA',
        'GABI': 'GABI',
        'FANNY': 'FANNY',
        'DENIZE': 'DENIZE',
        'DANISIO': 'DANISIO',
        'NATALIA': 'NATALIA'
        # Adicionar mais padronizações conforme necessário
    })
    
    # 5. Exportar o dataset final
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"Modelo de dados refinado salvo em: {OUTPUT_FILE}")
    
    # 6. Atualizar metadados
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    
    metadata["final_dataset_columns"] = list(df.columns)
    metadata["min_order_date"] = df['order_date'].min().strftime('%Y-%m-%d')
    metadata["max_order_date"] = df['order_date'].max().strftime('%Y-%m-%d')
    
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)
    print("Metadados atualizados.")

if __name__ == "__main__":
    refine_data_model()
