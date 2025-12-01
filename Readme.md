Passo 1: Preparação do Ambiente
Crie a Estrutura de Pastas:

desafio_analista_dados/
├── upload/
│   ├── clientes_crm.csv
│   ├── pedido_ecom.json
│   └── pedido_erp.csv
├── data_integration.py
├── data_modeling.py
├── kpi_calculation.py
└── dashboard_generator.py

Instale as Dependências:
Abra o terminal ou prompt de comando na pasta principal do projeto (desafio_analista_dados) e instale as bibliotecas Python necessárias. Recomenda-se o uso de um ambiente virtual (venv).
Bash
# Crie um ambiente virtual (opcional, mas recomendado)
python -m venv venv
# Ative o ambiente virtual
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate   # No Windows

# Instale as bibliotecas
pip install pandas dash plotly
Passo 2: Processamento e Integração dos Dados (ETL)
Você precisa rodar os scripts de processamento de dados na ordem correta para gerar o dataset final e os KPIs.
Integração dos Dados Brutos:
Este script (data_integration.py) limpa os documentos de cliente e unifica os pedidos de ERP e E-commerce, salvando o resultado em integrated_data.csv.
Bash
python data_integration.py
Modelagem e Enriquecimento:
Este script (data_modeling.py) carrega o arquivo integrado, cria colunas de tempo, padroniza nomes de vendedores e adiciona a flag de primeira compra, salvando o resultado final em final_dataset.csv.
Bash
python data_modeling.py
Cálculo dos Indicadores (KPIs):
Este script (kpi_calculation.py) calcula todas as métricas necessárias para o dashboard e as salva em kpis.json.
Bash
python kpi_calculation.py
Passo 3: Execução do Dashboard
Geração e Execução do Dashboard:
O script dashboard_generator.py é o coração do projeto. Ele carrega os dados processados e os KPIs, e inicia o servidor web do Dash.
Bash
python dashboard_generator.py
Acesso ao Dashboard:
Após rodar o comando, o terminal exibirá uma mensagem indicando que o servidor está rodando, geralmente em um endereço como:
Plain Text
Dash is running on http://127.0.0.1:8050/
Abra seu navegador e acesse o endereço fornecido para interagir com o dashboard.
Observação: O script dashboard_generator.py também gera um arquivo estático chamado dashboard.html na pasta principal, que é uma pré-visualização do layout inicial, mas a interatividade completa (como a aba do Vendedor ) só funciona ao rodar o servidor Dash.
Resumo da Ordem de Execução:
python data_integration.py
python data_modeling.py
python kpi_calculation.py
python dashboard_generator.py (para iniciar o servidor)