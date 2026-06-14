import re
import numpy as np

'''
A classe que contém as funções para determinação de um autômato Bruto a partir de 
uma simplificação em Wirth. Todas as funções retornam String, para ficar visual 
no terminal do arquivo principal, mas toda a lógica de construção é privada e interna.
Para criar a lógica, chamamos cada função dentro do arquivo principal que vai retornar uma string
e printar no console.
'''
class AutomatoBrutoClass(object):

    # Prod_Gramaticais = resultado de cada simplificação Wirth
    def __init__(self, prod_gramaticais: str) -> None:
        self.__prod_gramaticais = prod_gramaticais

        # Variáveis auxiliares para cada etapa do automato
        self.__lista_posicao, self.__lista_regras_estado, self.__transicoes = [], [], []
        self.__variavel = []  
        self.__estado_inicial, self.__estados_finais = "", []

    """ Determinar os estados do autômato
    1. Colocar posições de atribuição de estados entre cada símbolo da produção
    2. Aplicar regras de atribuição de estados
    """

    def __getProducao(self, tokens: list, index: int) -> list:
        return tokens[(index + 1):]

    def __getStringVariavel(self) -> str:
        return " ".join(str(var) for var in self.__variavel)

    def atribuirPosicao(self) -> str:

         # Separar os elementos com "" como um único token
        padrao_regex = r'"[^"]*"|\S+'
        tokens = re.findall(padrao_regex, self.__prod_gramaticais)

        index = tokens.index("=")
        self.__variavel = res = tokens[:index + 1] # Criando uma lista apenas com a variável

        # Adicionando um . entre cada token da produção
        for token in self.__getProducao(tokens, index):
            res.extend(['.', token]) 

        res.append(".")
        self.__lista_posicao = res

        return " ".join(res);

    """Regras de determinação de estado
    Regra 1: No inicio de cada possível cadeia atribuir o estado 0 fazer j=1
    Regra 2: Para agrupamentos entre parênteses ou colchetes propagar o estado anterior 
    ao agrupamento para todos os possíveis inícios e atribuir j ao estado após
    o agrupamento. Incrementar j
    Regra 3: Para agrupamentos entre chaves propagar o estado j para todos os possíveis 
    inícios e atribuir j ao final do agrupamento. Incrementar j
    Regra 4: Para terminais e não terminais isolados atribuir o estado j à direita do símbolo. 
    Incrementar j
    """
    def regrasEstado(self) -> str:

        j = 1
        estado_atual = 0
        pilha, resultado = [], []

        # Pegar todos os elementos da produção
        for token in self.__getProducao(self.__lista_posicao, self.__lista_posicao.index("=")):
            
            match token:

                case '.':
                    resultado.append(estado_atual)

                case '(' | '[':
                    resultado.append(token)
                    pilha.append((token, estado_atual, j))
                    j += 1
                
                case '{':
                    resultado.append(token)
                    estado_atual = j
                    pilha.append((token, estado_atual, j))
                    j += 1
                
                case '|':
                    resultado.append(token)
                    estado_atual = 0 if not pilha else pilha[-1][1] # Pegar o estado atual do último elemento da pilha
                
                case '}' | ')' | ']':
                    resultado.append(token)
                    estado_atual = pilha.pop()[2]
                
                case _:
                    resultado.append(token)
                    estado_atual = j
                    j += 1
        self.__lista_regras_estado = resultado
        return self.__getStringVariavel() + (str(resultado))
        
    """Regras de determinação de transições
    Regra 01: para cada ocorrência de símbolos terminais e não terminais criar transições 
    com consumo de átomo
    Regra 02: criar transições em vazio para cada opção de final do agrupamento entre parênteses 
    e colchetes ao estado do final do agrupamento
    Regra 03: criar transições em vazio para cada opção de final do agrupamento entre chaves para 
    o inicio das opções do mesmo agrupamento
    Regra 04: criar transições em vazio para agrupamentos entre colchetes e chaves dos estados 
    anteriores ao agrupamento para o estado posterior do agrupamento 
    (caráter opcional do agrupamento).
    """
    def determinarTransicoes(self) -> str:

        k = self.__lista_regras_estado
        pilha, transicoes_finais = [], []

        # Organizando uma tupla com (estado_origem, simbolo, estado_destino)
        transicoes = [(k[i-1], k[i], k[i+1]) for i in range(1, len(k), 2)]

        for t in transicoes:
  
            match t[1]:
                case '(' | '[' | '{':
                    pilha.append((t[1], t[0], t[2], [])) # (token, estado_origem, estado_destino, ramos_finais)

                case '|':
                    pilha[-1][3].append(t[0]) if pilha else ...# Adiciona em ramos_finais
                
                case ')' | ']' | '}':

                    pilha[-1][3].append(t[0])
                    j = pilha.pop()
                    
                    # No fechamento, o estado_destino de 't' é o estado logo após o agrupamento inteiro
                    estado_depois_fechamento = t[2]

                    token_abertura, estado_origem, estado_destino, ramos_finais = j[0], j[1], j[2], j[3]
                    for estado in ramos_finais:

                        if token_abertura in ['(', '[']:
                            transicoes_finais.append((estado, 'e', estado_depois_fechamento))
                        elif token_abertura == '{':
                            transicoes_finais.append((estado, 'e', estado_destino))

                    if token_abertura in ['[', '{']:
                        transicoes_finais.append((estado_origem, 'e', estado_depois_fechamento))

                case _:
                    transicoes_finais.append((t[0], t[1], t[2]))

        self.__transicoes = transicoes_finais
        return "\n".join(str(trans) for trans in transicoes_finais)


    """ DETERMINAÇÃO DO ESTADO INICIAL
    O estado inicial do autômato será sempre o estado 0.
    """
    def __determinarEstadoInicial(self) -> str:
        self.__estado_inicial = "0"

    """ DETERMINAÇÃO DOS ESTADOS FINAIS
    Captura os estados que antecedem os '|' no nível global da regra e o estado final absoluto.
    """
    def __determinarEstadosFinais(self) -> str:
        finais = []
        nivel_agrupamento = 0

        for i, elemento in enumerate(self.__lista_regras_estado):
            if elemento in ['(', '[', '{']:
                nivel_agrupamento += 1
            elif elemento in [')', ']', '}']:
                nivel_agrupamento -= 1
            elif elemento == '|' and nivel_agrupamento == 0:
                # Se houver um '|' na raiz, o estado imediatamente anterior a ele é final
                if i > 0 and isinstance(self.__lista_regras_estado[i-1], int):
                    finais.append(self.__lista_regras_estado[i-1])

        # O último elemento da lista de estados estruturada sempre representará o fim da última ramificação
        if self.__lista_regras_estado and isinstance(self.__lista_regras_estado[-1], int):
            finais.append(self.__lista_regras_estado[-1])

        # Remove duplicados e ordena numericamente
        self.__estados_finais = sorted(list(set(finais)))
    
    # Função unificadora solicitada no escopo original que envelopa os retornos em String/Lista
    def determinarEstados(self) -> tuple[str, list]:
        self.__determinarEstadoInicial()
        self.__determinarEstadosFinais()
        return self.__estado_inicial, self.__estados_finais
    
    """ AUTÔMATO EM FORMATO DE TABELA
    Gera a tabela de transições cruzando os Estados (linhas) com os Símbolos do Alfabeto (colunas).
    """
    def montarTabelaTransicoes(self) -> tuple[str, np.ndarray]:
        estados = set()
        alfabeto = set()

        for orig, symb, dest in self.__transicoes:
            estados.add(orig)
            estados.add(dest)
            if symb != 'e':
                alfabeto.add(symb)

        estados.add(0) 
        lista_estados = sorted(list(estados))
        lista_alfabeto = sorted(list(alfabeto)) + ['e']

        matriz_transicao = {est: {symb: [] for symb in lista_alfabeto} for est in lista_estados}

        for orig, symb, dest in self.__transicoes:
            if dest not in matriz_transicao[orig][symb]:
                matriz_transicao[orig][symb].append(dest)
                matriz_transicao[orig][symb].sort()

        # Construindo visualização textual
        cabecalho = ["Estado"] + lista_alfabeto
        linhas_tabela = []
        linhas_tabela.append(" | ".join(f"{col:^10}" for col in cabecalho))
        linhas_tabela.append("-" * len(linhas_tabela[0]))

        # Construindo estrutura para NumPy
        matriz_np = [cabecalho]

        for est in lista_estados:
            prefixo = ""
            if str(est) == self.__estado_inicial:
                prefixo += "->"
            if est in self.__estados_finais:
                prefixo += "*"

            est_formatado = f"{prefixo}{est}"
            linha_txt = [f"{est_formatado:<10}"]
            linha_np = [est_formatado] # Identificador do estado na matriz exportada

            for symb in lista_alfabeto:
                celula_destinos = matriz_transicao[est][symb]
                celula_str = str(celula_destinos) if celula_destinos else "[]"
                
                linha_txt.append(f"{celula_str:^10}")
                linha_np.append(celula_str)

            linhas_tabela.append(" | ".join(linha_txt))
            matriz_np.append(linha_np)

        string_visual = "\n".join(linhas_tabela)
        array_numpy = np.array(matriz_np, dtype=object)

        return string_visual, array_numpy