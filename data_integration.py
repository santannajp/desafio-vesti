import pandas as pd
import json
import re

# Definindo o caminho dos arquivos
CRM_FILE = "upload\clientes_crm.csv"
ERP_FILE = "upload\pedido_erp.csv"
ECOM_FILE = "upload\pedido_ecom.json"
OUTPUT_FILE = "upload/integrated_data.csv"

# --- Funções de Limpeza e Transformação ---

def clean_document(doc):
    """Remove caracteres não numéricos do documento (CPF/CNPJ)."""
    if pd.isna(doc):
        return None
    # Remove caracteres não numéricos, mas mantém a string
    cleaned = re.sub(r'\D', '', str(doc))
    # Trata casos especiais como o do arquivo CRM (ex: (43) 99181-8183)
    if len(cleaned) not in [11, 14]:
        return None
    return cleaned

def load_and_clean_crm(file_path):
    """Carrega e limpa os dados do CRM."""
    print("Carregando dados do CRM...")
    # O arquivo CSV usa ';' como separador e tem um byte de ordem de marca (BOM)
    df_crm = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
    
    # Renomear colunas para padronização
    df_crm.rename(columns={
        'id': 'customer_id',
        'document': 'customer_document',
        'seller_name': 'crm_seller_name',
        'created_at': 'crm_created_at'
    }, inplace=True)
    
    # Limpar a coluna de documento
    df_crm['customer_document'] = df_crm['customer_document'].apply(clean_document)
    
    # Selecionar colunas relevantes e remover duplicatas baseadas no documento
    df_crm = df_crm[['customer_id', 'customer_document', 'name', 'email', 'status', 'buy', 'crm_seller_name', 'crm_created_at']].drop_duplicates(subset=['customer_document'])
    
    print(f"CRM carregado: {len(df_crm)} registros.")
    return df_crm

def load_and_clean_erp(file_path):
    """Carrega e limpa os dados de pedidos do ERP (Vendas Físicas)."""
    print("Carregando dados do ERP...")
    df_erp = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
    
    # Renomear colunas para padronização
    df_erp.rename(columns={
        'id': 'order_id',
        'order_value': 'total_value',
        'order_created': 'order_date',
        'seller_name': 'seller_name'
    }, inplace=True)
    
    # Limpar a coluna de documento
    df_erp['customer_document'] = df_erp['customer_document'].apply(clean_document)
    
    # Converter 'total_value' para numérico (substituir ',' por '.')
    df_erp['total_value'] = df_erp['total_value'].str.replace(',', '.', regex=False).astype(float)
    
    # Adicionar coluna de origem
    df_erp['source'] = 'ERP_Fisica'
    
    # Selecionar colunas relevantes
    df_erp = df_erp[['order_id', 'customer_document', 'seller_name', 'total_value', 'order_date', 'source']]
    
    print(f"ERP carregado: {len(df_erp)} registros.")
    return df_erp

def load_and_clean_ecom(file_path):
    """Carrega e limpa os dados de pedidos do E-commerce (Vendas Online)."""
    print("Carregando dados do E-commerce...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extrair dados relevantes
    orders_list = []
    for doc in data.get('docs', []):
        order_id = doc.get('_id')
        customer_doc = doc.get('customer', {}).get('doc')
        order_date = doc.get('settings', {}).get('createdAt')
        source = doc.get('settings', {}).get('source')
        seller_name = doc.get('seller', {}).get('name')
        total_value = doc.get('summary', {}).get('total')
        
        orders_list.append({
            'order_id': order_id,
            'customer_document': customer_doc,
            'seller_name': seller_name,
            'total_value': total_value,
            'order_date': order_date,
            'source': source
        })
        
    df_ecom = pd.DataFrame(orders_list)
    
    # Limpar a coluna de documento
    df_ecom['customer_document'] = df_ecom['customer_document'].apply(clean_document)
    
    # Converter 'total_value' para numérico (já deve ser float, mas garante)
    df_ecom['total_value'] = pd.to_numeric(df_ecom['total_value'], errors='coerce')
    
    # Selecionar colunas relevantes
    df_ecom = df_ecom[['order_id', 'customer_document', 'seller_name', 'total_value', 'order_date', 'source']]
    
    print(f"E-commerce carregado: {len(df_ecom)} registros.")
    return df_ecom

# --- Integração e Exportação ---

def integrate_data():
    """Função principal para carregar, limpar e integrar os dados."""
    
    # 1. Carregar e limpar os dados
    df_crm = load_and_clean_crm(CRM_FILE)
    df_erp = load_and_clean_erp(ERP_FILE)
    df_ecom = load_and_clean_ecom(ECOM_FILE)
    
    # 2. Unir os pedidos (ERP + E-commerce)
    df_orders = pd.concat([df_erp, df_ecom], ignore_index=True)
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'], format='mixed', utc=True).dt.tz_convert(None) # Converter para datetime e remover timezone
    
    print(f"Total de pedidos unificados: {len(df_orders)}.")
    
    # 3. Integrar com os dados do CRM
    # Usar o 'customer_document' como chave de ligação
    df_integrated = pd.merge(
        df_orders, 
        df_crm, 
        on='customer_document', 
        how='left', # Manter todos os pedidos, mesmo que o cliente não esteja no CRM (para análise de novos clientes)
        suffixes=('_order', '_crm')
    )
    
    # 4. Limpeza final e preparação
    # Preencher 'customer_id' e 'name' para clientes que não estão no CRM (se necessário, para evitar NAs)
    # Para este desafio, vamos manter os NAs para identificar clientes não cadastrados no CRM.
    
    # 5. Exportar o dataset integrado
    print(f"Total de registros integrados: {len(df_integrated)}.")
    df_integrated.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"Dados integrados salvos em: {OUTPUT_FILE}")
    
    # 6. Salvar um resumo da estrutura para a próxima fase
    # Criar um arquivo de metadados simples
    metadata = {
        "total_orders": len(df_orders),
        "total_customers_in_crm": len(df_crm),
        "total_integrated_records": len(df_integrated),
        "columns": list(df_integrated.columns)
    }
    with open("upload/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=4)
    print("Metadados salvos.")

if __name__ == "__main__":
    integrate_data()
