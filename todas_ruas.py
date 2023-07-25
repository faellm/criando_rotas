from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import folium
import numpy as np

app = Flask(__name__)

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dicionário com os bairros das cidades
bairros_por_cidade = {

    'Curitiba': [
        'Bairro 1 - Curitiba',
        'Bairro 2 - Curitiba',
        'Bairro 3 - Curitiba',
    ],

    'São José dos Pinhais': [
        'Academia',
        'Afonso Pena',
        'Águas Belas',
        'Área Institucional Aeroportuária',
        'Aristocrata',
        'Arujá',
        'Aviação',
        'Barro Preto',
        'Bom Jesus',
        'Boneca do Iguaçu',
        'Borda do Campo',
        'Cachoeira',
        'Campina do Taquaral',
        'Campo Largo da Roseira',
        'Centro',
        'Cidade Jardim',
        'Colônia Rio Grande',
        'Contenda',
        'Costeira',
        'Cristal',
        'Cruzeiro',
        'Del Rey',
        'Dom Rodrigo',
        'Guatupê',
        'Iná',
        'Ipê',
        'Itália',
        'Jurema',
        'Miringuava',
        'Ouro Fino',
        'Parque da Fonte',
        'Pedro Moro',
        'Quissisana',
        'Rio Pequeno',
        'Roseira de São Sebastião',
        'Santo Antônio',
        'São Cristóvão',
        'São Domingos',
        'São Marcos',
        'São Pedro',
        'Zacarias',
    ]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        return generate_map(cidade, bairro)

    return render_template('teste_index.html')

def get_bairros(cidade):
    # Retornar os bairros específicos da cidade selecionada
    return bairros_por_cidade.get(cidade, [])

@app.route('/bairros', methods=['GET'])
def get_bairros_json():
    cidade = request.args.get('cidade')
    bairros = get_bairros(cidade)
    return jsonify({'bairros': bairros})

def generate_map(bairro, cidade):
    # Obter o grafo de ruas do bairro usando o OSM
    G = ox.graph_from_place(bairro + ", " + cidade, network_type='drive')

    # Verificar se o grafo é fortemente conectado
    if not nx.is_strongly_connected(G):
        # Dividir o grafo em componentes conectados
        componentes_conectados = list(nx.strongly_connected_components(G))

        # Inicializar uma lista para armazenar as rotas dos componentes
        rotas = []

        # Encontrar uma rota para cada componente
        for componente in componentes_conectados:
            subgrafo = G.subgraph(componente)
            if nx.is_eulerian(subgrafo.to_undirected()):
                # Se o componente é Euleriano, usar a rota euleriana
                rota = [u for u, v in nx.eulerian_circuit(subgrafo.to_undirected())]
            else:
                # Caso contrário, usar a rota aproximada (vizinho mais próximo)
                rota = nx.approximation.traveling_salesman_problem(subgrafo, cycle=True, method='nearest_neighbor')

            rotas.extend(rota)

        # Verificar se existe uma aresta entre o último nó da última rota e o primeiro nó da primeira rota
        if G.has_edge(rotas[-1], rotas[0]):
            # Se existe, adicionar a primeira aresta de volta ao último nó para formar um ciclo
            rotas.append(rotas[0])

    else:
        # Se o grafo é fortemente conectado, calcular a rota usando a abordagem anterior (Euleriana)
        # Calcular o circuito Euleriano (rota) que passa por todas as arestas
        rotas = [u for u, v in nx.eulerian_circuit(G.to_undirected())]

        # Adicionar a primeira aresta de volta ao último nó para formar um ciclo
        rotas.append(rotas[0])

    # Obter as coordenadas dos pontos da rota
    lats, lons = zip(*[(G.nodes[node]['y'], G.nodes[node]['x']) for node in rotas])

if __name__ == '__main__':
    app.run(debug=True)