# Desafio Analista de Dados: Pipeline ETL e Dashboard

Este repositório contém o projeto para o desafio de analista de dados, que consiste em um pipeline de **ETL (Extração, Transformação e Carga)** para integrar dados de diferentes fontes e um **Dashboard** interativo construído com **Dash/Plotly** para visualização dos principais indicadores de desempenho (KPIs).

## 1. Preparação do Ambiente

### 1.1. Estrutura de Pastas

A estrutura de pastas do projeto deve ser a seguinte:

```
desafio_analista_dados/
├── upload/
│   ├── clientes_crm.csv
│   ├── pedido_ecom.json
│   └── pedido_erp.csv
├── data_integration.py
├── data_modeling.py
├── kpi_calculation.py
└── dashboard_generator.py
```

### 1.2. Instalação das Dependências

Abra o terminal ou prompt de comando na pasta principal do projeto (`desafio_analista_dados`) e instale as bibliotecas Python necessárias. É **altamente recomendado** o uso de um ambiente virtual (`venv`).

1.  **Crie e Ative o Ambiente Virtual (Opcional):**

    ```bash
    # Crie um ambiente virtual
    python -m venv venv
    
    # Ative o ambiente virtual (Linux/macOS)
    source venv/bin/activate
    
    # Ative o ambiente virtual (Windows)
    # venv\Scripts\activate
    ```

2.  **Instale as Bibliotecas:**

    ```bash
    pip install pandas dash plotly
    ```

## 2. Processamento e Integração dos Dados (ETL)

Você deve rodar os scripts de processamento de dados na ordem correta para gerar o dataset final e os KPIs.

### 2.1. Integração dos Dados Brutos

-   **Script:** `data_integration.py`
-   **Função:** Limpa os documentos de cliente e unifica os pedidos de ERP e E-commerce.
-   **Saída:** Salva o resultado em `integrated_data.csv`.

```bash
python data_integration.py
```

### 2.2. Modelagem e Enriquecimento

-   **Script:** `data_modeling.py`
-   **Função:** Carrega o arquivo integrado, cria colunas de tempo, padroniza nomes de vendedores e adiciona a *flag* de primeira compra.
-   **Saída:** Salva o resultado final em `final_dataset.csv`.

```bash
python data_modeling.py
```

### 2.3. Cálculo dos Indicadores (KPIs)

-   **Script:** `kpi_calculation.py`
-   **Função:** Calcula todas as métricas necessárias para o dashboard.
-   **Saída:** Salva os indicadores em `kpis.json`.

```bash
python kpi_calculation.py
```

## 3. Execução do Dashboard

### 3.1. Geração e Execução do Dashboard

O script `dashboard_generator.py` é o coração do projeto. Ele carrega os dados processados e os KPIs, e inicia o servidor web do Dash.

```bash
python dashboard_generator.py
```

### 3.2. Acesso ao Dashboard

Após rodar o comando, o terminal exibirá uma mensagem indicando que o servidor está rodando, geralmente em um endereço como:

```
Dash is running on http://127.0.0.1:8050/
```

Abra seu navegador e acesse o endereço fornecido para interagir com o dashboard.

> **Observação:** O script `dashboard_generator.py` também gera um arquivo estático chamado `dashboard.html` na pasta principal. Este arquivo é apenas uma pré-visualização do layout inicial. A interatividade completa (como a aba do Vendedor) só funciona ao rodar o servidor Dash.

## Resumo da Ordem de Execução

Para garantir o funcionamento correto do pipeline, execute os scripts na seguinte ordem:

```bash
python data_integration.py
python data_modeling.py
python kpi_calculation.py
python dashboard_generator.py  # Para iniciar o servidor e acessar o dashboard
```
