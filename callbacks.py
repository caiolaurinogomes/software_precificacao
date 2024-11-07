from dash import Input, Output, State, dcc, html
import pandas as pd
import numpy as np
import base64
import io
from flask_login import current_user
from preprocessing import process_data
from pricing_logic import calculate_prices
from generate_table import generate_pricing_table
from database import get_db
from models import Input as UserInput

# Variáveis globais para armazenar os dados processados
global_df = None
global_df_faixas = None
global_pricing_table = None  # Variável para a tabela de precificação
global_product_table = None  # Variável para a tabela de produtos

def register_callbacks(app):
   
    # Callback para carregar dados e atualizar os gráficos e indicadores
    @app.callback(
        [Output('oferta-graph', 'figure'),
         Output('giro-graph', 'figure'),
         Output('desconto-medio', 'children'),
         Output('desconto-medio-ponderado', 'children'),
         Output('giro-medio', 'children'),
         Output('error-message', 'children')],
        Input('upload-data', 'contents'),
        prevent_initial_call=True
    )
    def update_graphs(contents):
        global global_df, global_df_faixas, global_product_table, global_pricing_table
        if contents is None:
            return {}, {}, "Desconto Médio Vendidos:", "Desconto Médio Estoque:", "Giro Médio Vendidos:", ""
       
        error_message = ""
 
        # Decodifica o conteúdo do arquivo carregado
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
       
        try:
            # Lê o conteúdo como DataFrame
            df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            error_message = f"Erro ao carregar o arquivo: {e}"
            return {}, {}, "Desconto Médio Vendidos:", "Desconto Médio Estoque:", "Giro Médio Vendidos:", error_message
       
        try:
            # Processa os dados e calcula indicadores
            df, df_faixas, desconto_medio, desconto_medio_ponderado, giro_medio_percent = process_data(df)
        except Exception as e:
            error_message = f"Erro ao processar os dados: {e}"
            return {}, {}, "Desconto Médio Vendidos:", "Desconto Médio Estoque:", "Giro Médio Vendidos:", error_message
       
        # Atualiza as variáveis globais para exportação
        global_df = df
        global_df_faixas = df_faixas
 
        # Gera a tabela de precificação com parâmetros padrão
        default_params = {
            'step_giro_up': 2.0,
            'step_giro_down': 2.0,
            'step_discount_up': 2.0,
            'step_discount_down': 2.0,
            'curve_shift': 0.0
        }
        global_pricing_table = generate_pricing_table(**default_params)
 
        # Cria a tabela de produtos com as colunas especificadas
        product_table = df[['codigo', 'giro', 'desconto', 'preco_original', 'delta_giro']].copy()
        product_table['giro'] = product_table['giro'] * 100
        product_table['delta_giro'] = product_table['delta_giro'] * 100

        # Salva os dados do input no banco de dados associado ao usuário
        db = next(get_db())
        novo_input = UserInput(user_id=current_user.id, data=contents)
        db.add(novo_input)
        db.commit()

        # Encontrar o "Desconto Adicional Calibrado" correspondente para cada produto
        pricing_table = global_pricing_table.copy()
        pricing_table['Delta Giro (p.p)'] = pricing_table['Delta Giro (p.p)'].astype(float)
        pricing_table['Desconto Adicional Calibrado'] = pricing_table['Desconto Adicional Calibrado'].astype(float)
 
        delta_giro_array = pricing_table['Delta Giro (p.p)'].values
 
        def find_nearest(value, array):
            idx = (np.abs(array - value)).argmin()
            return array[idx]
 
        desconto_adicional_calibrado = []
        for delta in product_table['delta_giro']:
            nearest_delta = find_nearest(delta, delta_giro_array)
            desconto_calibrado = pricing_table.loc[pricing_table['Delta Giro (p.p)'] == nearest_delta, 'Desconto Adicional Calibrado'].values[0]
            desconto_adicional_calibrado.append(desconto_calibrado)
 
        product_table['Desconto Adicional Calibrado'] = desconto_adicional_calibrado
        product_table['novo_desconto'] = product_table['desconto'] * (1 + (product_table['Desconto Adicional Calibrado'] / 100))
 
        desconto_minimo = 0.0
        desconto_maximo = 100.0
        product_table['novo_desconto'] = product_table['novo_desconto'].clip(lower=desconto_minimo, upper=desconto_maximo)
        product_table['novo_preco'] = product_table['novo_desconto'] * product_table['preco_original']
 
        global_product_table = product_table
 
        oferta_fig = create_oferta_graph(df_faixas)
        giro_fig = create_giro_graph(df)
 
        desconto_text = f"Desconto Médio Vendidos: {desconto_medio:.1f}%"
        desconto_ponderado_text = f"Desconto Médio Estoque: {desconto_medio_ponderado:.1f}%"
        giro_text = f"Giro Médio Vendidos: {giro_medio_percent:.1f}%"
       
        return oferta_fig, giro_fig, desconto_text, desconto_ponderado_text, giro_text, error_message
 
    # Callback para atualizar a tabela de precificação e a tabela de produtos quando os parâmetros mudam
    @app.callback(
        Output('hidden-div', 'children'),  # Div escondido apenas para acionar o callback
        [
            Input('step-desconto-cima', 'value'),
            Input('step-desconto-baixo', 'value'),
            Input('step-giro-cima', 'value'),
            Input('step-giro-baixo', 'value'),
            Input('deslocamento-curva', 'value'),
            Input('desconto-minimo', 'value'),  # Novo Input para Desconto Mínimo
            Input('desconto-maximo', 'value')   # Novo Input para Desconto Máximo
        ],
        State('hidden-div', 'children')  # Estado para evitar loop infinito
    )
    def update_tables(
        step_desconto_cima,
        step_desconto_baixo,
        step_giro_cima,
        step_giro_baixo,
        deslocamento_curva,
        desconto_minimo,  # Recebendo Desconto Mínimo
        desconto_maximo,  # Recebendo Desconto Máximo
        _
    ):
        global global_pricing_table, global_product_table, global_df
 
        # Definindo valores padrão caso sejam None
        if desconto_minimo is None:
            desconto_minimo = 0.0
        if desconto_maximo is None:
            desconto_maximo = 100.0
 
        if None in [step_desconto_cima, step_desconto_baixo, step_giro_cima, step_giro_baixo, deslocamento_curva]:
            step_desconto_cima = 2.0
            step_desconto_baixo = 2.0
            step_giro_cima = 2.0
            step_giro_baixo = 2.0
            deslocamento_curva = 0.0
 
        global_pricing_table = generate_pricing_table(
            step_giro_up=step_giro_cima,
            step_giro_down=step_giro_baixo,
            step_discount_up=step_desconto_cima,
            step_discount_down=step_desconto_baixo,
            curve_shift=deslocamento_curva
        )
 
        if global_df is not None:
            product_table = global_df[['codigo', 'giro', 'desconto', 'preco_original', 'delta_giro']].copy()
            product_table['giro'] = product_table['giro'] * 100
            product_table['delta_giro'] = product_table['delta_giro'] * 100
 
            pricing_table = global_pricing_table.copy()
            pricing_table['Delta Giro (p.p)'] = pricing_table['Delta Giro (p.p)'].astype(float)
            pricing_table['Desconto Adicional Calibrado'] = pricing_table['Desconto Adicional Calibrado'].astype(float)
 
            delta_giro_array = pricing_table['Delta Giro (p.p)'].values
 
            def find_nearest(value, array):
                idx = (np.abs(array - value)).argmin()
                return array[idx]
 
            desconto_adicional_calibrado = []
            for delta in product_table['delta_giro']:
                nearest_delta = find_nearest(delta, delta_giro_array)
                desconto_calibrado = pricing_table.loc[pricing_table['Delta Giro (p.p)'] == nearest_delta, 'Desconto Adicional Calibrado'].values[0]
                desconto_adicional_calibrado.append(desconto_calibrado)
 
            product_table['Desconto Adicional Calibrado'] = desconto_adicional_calibrado
            product_table['novo_desconto'] = product_table.apply(
                lambda row: desconto_maximo if row['giro'] == 0 else row['desconto'] * (1 + (row['Desconto Adicional Calibrado'] / 100)),
                axis=1
            )
 
            product_table['novo_desconto'] = product_table['novo_desconto'].clip(lower=desconto_minimo, upper=desconto_maximo)
            product_table['novo_preco'] = (1 - product_table['novo_desconto']) * product_table['preco_original']
 
            product_table = product_table.merge(
                global_df[['codigo', 'estoque_atual']],
                on='codigo',
                how='left'
            )
 
            product_table = product_table[product_table['estoque_atual'] > 0]
 
            global_product_table = product_table
 
        return ''
   
    @app.callback(
        Output("download-dataframe-xlsx", "data"),
        Input("export-button", "n_clicks"),
        prevent_initial_call=True
    )
    def export_data(n_clicks):
        global global_df, global_df_faixas, global_pricing_table, global_product_table
        if global_df is None or global_df_faixas is None or global_pricing_table is None or global_product_table is None:
            return None
       
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            global_df.to_excel(writer, index=False, sheet_name="Dados")
            global_df_faixas.to_excel(writer, index=False, sheet_name="Faixas")
            global_pricing_table.to_excel(writer, index=False, sheet_name="Tabela Precificação")
            global_product_table.to_excel(writer, index=False, sheet_name="Tabela Produtos")
       
        output.seek(0)
       
        return dcc.send_bytes(output.getvalue(), filename="planilha_exportada.xlsx")
 
    @app.callback(
        Output('step-desconto-cima', 'value'),
        [Input('increment-desconto-cima', 'n_clicks'), Input('decrement-desconto-cima', 'n_clicks')],
        State('step-desconto-cima', 'value')
    )
    def update_step_desconto_cima(increment, decrement, current_value):
        increment = increment or 0
        decrement = decrement or 0
        if increment > decrement:
            return round(current_value + 0.1, 1)
        elif decrement > increment:
            return max(round(current_value - 0.1, 1), 0)
        return current_value
 
    @app.callback(
        Output('step-desconto-baixo', 'value'),
        [Input('increment-desconto-baixo', 'n_clicks'), Input('decrement-desconto-baixo', 'n_clicks')],
        State('step-desconto-baixo', 'value')
    )
    def update_step_desconto_baixo(increment, decrement, current_value):
        increment = increment or 0
        decrement = decrement or 0
        if increment > decrement:
            return round(current_value + 0.1, 1)
        elif decrement > increment:
            return max(round(current_value - 0.1, 1), 0)
        return current_value
 
    @app.callback(
        Output('step-giro-cima', 'value'),
        [Input('increment-giro-cima', 'n_clicks'), Input('decrement-giro-cima', 'n_clicks')],
        State('step-giro-cima', 'value')
    )
    def update_step_giro_cima(increment, decrement, current_value):
        increment = increment or 0
        decrement = decrement or 0
        if increment > decrement:
            return round(current_value + 0.1, 1)
        elif decrement > increment:
            return max(round(current_value - 0.1, 1), 0)
        return current_value
 
    @app.callback(
        Output('step-giro-baixo', 'value'),
        [Input('increment-giro-baixo', 'n_clicks'), Input('decrement-giro-baixo', 'n_clicks')],
        State('step-giro-baixo', 'value')
    )
    def update_step_giro_baixo(increment, decrement, current_value):
        increment = increment or 0
        decrement = decrement or 0
        if increment > decrement:
            return round(current_value + 0.1, 1)
        elif decrement > increment:
            return max(round(current_value - 0.1, 1), 0)
        return current_value
 
    def create_oferta_graph(df_faixas):
        import plotly.graph_objs as go
        non_zero_indexes = df_faixas['qtd_produtos'].to_numpy().nonzero()[0]
        if non_zero_indexes.size > 0:
            df_faixas_filtered = df_faixas.iloc[non_zero_indexes[0]: non_zero_indexes[-1] + 1]
        else:
            df_faixas_filtered = df_faixas
 
        faixa_labels = [f'{int(faixa.left * 100)}-{int(faixa.right * 100)}%' for faixa in df_faixas_filtered['faixa']]
        oferta_fig = go.Figure()
 
        oferta_fig.add_trace(go.Bar(
            x=faixa_labels,
            y=df_faixas_filtered['qtd_produtos'],
            name="Quantidade de Produtos",
            marker=dict(color='#4a90e2'),
            yaxis="y1"
        ))
        oferta_fig.add_trace(go.Scatter(
            x=faixa_labels,
            y=df_faixas_filtered['estoque_inicial'],
            mode='lines+markers',
            name="Estoque Inicial",
            line=dict(color='red'),
            yaxis="y2"
        ))
        oferta_fig.add_trace(go.Scatter(
            x=faixa_labels,
            y=df_faixas_filtered['estoque_atual'],
            mode='lines+markers',
            name="Estoque Atual",
            line=dict(color='green'),
            yaxis="y2"
        ))
 
        oferta_fig.update_layout(
            title="Oferta de Produtos por Faixa de Desconto",
            xaxis_title="Faixas de Desconto (%)",
            yaxis=dict(
                title="Quantidade de Produtos",
                titlefont=dict(color="#4a90e2"),
                tickfont=dict(color="#4a90e2")
            ),
            yaxis2=dict(
                title="Quantidade em Estoque",
                overlaying="y",
                side="right",
                titlefont=dict(color="black"),
                tickfont=dict(color="black")
            ),
            template="plotly_white"
        )
 
        return oferta_fig
 
    def create_giro_graph(df):
        import plotly.graph_objs as go
        giro_fig = go.Figure()
        giro_fig.add_trace(go.Scatter(
            x=df['desconto'] * 100,
            y=df['giro'] * 100,
            mode='markers',
            name="Giro",
            marker=dict(color='#4a90e2')
        ))
        giro_fig.update_layout(
            title="Relação entre Giro e Desconto",
            xaxis_title="Desconto (%)",
            yaxis_title="Giro (%)",
            template="plotly_white"
        )
        return giro_fig
