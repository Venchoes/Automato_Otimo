from models.AutomatoBruto import AutomatoBrutoClass as ABC
import copy

class AutomatoOtimoClass(ABC):
    def __init__(self, prod_gramaticais: str) -> None:
        super().__init__(prod_gramaticais)

    @classmethod
    def fromBruto(cls, bruto):
        nova_instancia = cls(bruto._prod_gramaticais)

        # COPIANDO OS DADOS DO PAI
        nova_instancia._tabela = copy.deepcopy(bruto._tabela)
        nova_instancia._estado_inicial = bruto._estado_inicial
        
        # Como _estados_finais é uma lista, fazemos uma cópia para não mexer na original
        nova_instancia._estados_finais = list(bruto._estados_finais)

        return nova_instancia

    def __calcularFechoVazio(self, estado_origem) -> list:
        """
        Função auxiliar para a Regra 3 (Recursividade).
        Busca em Profundidade (DFS) para encontrar todos os estados alcançáveis apenas por 'e'.
        """

        fecho = set()
        pilha = [estado_origem]

        while pilha:
            estado_atual = pilha.pop()
            if estado_atual not in fecho:
                fecho.add(estado_atual)
                # Adiciona à pilha todos os destinos alcançáveis por 'e' a partir do estado_atual
                destinos_vazios = self._tabela.get(estado_atual, {}).get('e', [])
                for dest in destinos_vazios:
                    if dest not in fecho:
                        pilha.append(dest)
        
        return list(fecho)


    def eliminar_transicoes_vazio(self):
        """
        Aplica as 4 regras de eliminação de transições em vazio do Autômato Ótimo.
        """
        # 1. Mapear o alcance total de todos os estados (Fecho-Epsilon)
        mapa_fechos = {}
        for estado in self._tabela:
            mapa_fechos[estado] = self.__calcularFechoVazio(estado)

        # 2 e 3. Aplicar herança de transições (Regra 1) e estados finais (Regra 2)
        for emissor in self._tabela:
            receptores = mapa_fechos[emissor]

            for receptor in receptores:
                if emissor == receptor:
                    continue # Ignora a cópia para si mesmo
                
                # --- APLICANDO REGRA 2 ---
                if receptor in self._estados_finais and emissor not in self._estados_finais:
                    self._estados_finais.append(emissor)
                
                # --- APLICANDO REGRA 1 ---
                for simbolo, destinos in self._tabela[receptor].items():
                    if simbolo != 'e': # Não copiamos os caminhos vazios, apenas o alfabeto real
                        for dest in destinos:
                            # Se o emissor ainda não tem esse destino para esse símbolo, adicionamos
                            if dest not in self._tabela[emissor][simbolo]:
                                self._tabela[emissor][simbolo].append(dest)
                                self._tabela[emissor][simbolo].sort() # Mantém a tabela organizada

        # Organiza os estados finais que podem ter ficado bagunçados na Regra 2
        self._estados_finais = sorted(list(set(self._estados_finais)))

        # 4. APLICANDO REGRA 4: Deletar a coluna 'e' da matriz de dicionários
        for estado in self._tabela:
            if 'e' in self._tabela[estado]:
                del self._tabela[estado]['e']


    def eliminar_transicoes_nao_deterministicas(self):

        alfabeto = set()
        for transicoes in self._tabela.values():
            alfabeto.update(transicoes.keys())

        # Fila para atender à REGRA 4 (recursividade)
        # Começamos com os estados originais da tabela
        estados_para_processar = list(self._tabela.keys())
        estados_processados = set()

        while estados_para_processar:
            estado_atual = estados_para_processar.pop(0)
            
            if estado_atual in estados_processados:
                continue

            estados_processados.add(estado_atual)
            linha_atual = self._tabela.get(estado_atual, {})

            for simbolo, destinos in linha_atual.items():

                if len(destinos) > 1: # Transação não determinística
                    # REGRA 1: Criar um estado associado ao conjunto
                    # Transformamos a lista [1, 2] em uma tupla (1, 2) que serve de chave
                    novo_estado_tupla = tuple(sorted(destinos, key=str))
                    self._tabela[estado_atual][simbolo] = [novo_estado_tupla]

                    if novo_estado_tupla not in self._tabela:
                        # Inicializa a linha vazia para o novo estado
                        self._tabela[novo_estado_tupla] = {symb: [] for symb in alfabeto}
                        
                        # REGRA 2: Preencher a linha com a união das linhas dos componentes
                        for estado_componente in novo_estado_tupla:
                            linha_componente = self._tabela.get(estado_componente, {})
                            
                            for s in alfabeto:
                                destinos_componente = linha_componente.get(s, [])
                                
                                # Faz a união evitando duplicatas
                                for dest in destinos_componente:
                                    if dest not in self._tabela[novo_estado_tupla][s]:
                                        self._tabela[novo_estado_tupla][s].append(dest)
                                        
                        # Mantém a organização visual da tabela
                        for s in alfabeto:
                            self._tabela[novo_estado_tupla][s].sort(key=str)
                            
                        # REGRA 3: Se algum componente for final, o novo também será
                        for estado_componente in novo_estado_tupla:
                            if estado_componente in self._estados_finais:
                                if novo_estado_tupla not in self._estados_finais:
                                    self._estados_finais.append(novo_estado_tupla)
                                break # Achou um final, já satisfaz a regra
                                
                        # REGRA 4: Adiciona o novo estado na fila para ser analisado
                        estados_para_processar.append(novo_estado_tupla)


    def eliminar_estados_nao_acessiveis(self):
        """
        Rastreia os caminhos a partir do estado inicial e deleta os estados inatingíveis.
        """
        # 1. Encontrar a chave real do estado inicial na tabela
        # (O Python pode ter chaves int ou str, isso garante que pegaremos a correta)
        chave_inicial = None
        for est in self._tabela.keys():
            if str(est) == str(self._estado_inicial):
                chave_inicial = est
                break
                
        # Trava de segurança: se o inicial sumiu, o autômato quebrou
        if chave_inicial is None:
            return

        # Conjunto para armazenar quem conseguimos alcançar (O(1) de tempo de busca)
        estados_acessiveis = set([chave_inicial])
        
        # Pilha para nossa Busca em Profundidade (DFS)
        pilha = [chave_inicial]

        # 2. Rastreamento: Navegar por todas as rotas possíveis
        while pilha:
            estado_atual = pilha.pop()
            linha_atual = self._tabela.get(estado_atual, {})
            
            # Vasculha todos os símbolos e seus destinos
            for simbolo, destinos in linha_atual.items():
                for dest in destinos:
                    if dest not in estados_acessiveis:
                        estados_acessiveis.add(dest)
                        pilha.append(dest) # Coloca na pilha para explorar os "filhos" dele depois

        # 3. Varredura: Identificar e deletar as "ilhas isoladas"
        # Precisamos criar uma lista estática das chaves para não dar erro
        # ao deletar itens de um dicionário enquanto iteramos sobre ele.
        estados_originais = list(self._tabela.keys())
        
        for est in estados_originais:
            if est not in estados_acessiveis:
                del self._tabela[est] # Apaga da tabela!

        # 4. Limpeza: Atualizar a lista de estados finais
        # Retém apenas os estados finais que sobreviveram ao corte
        finais_atualizados = []
        for est_final in self._estados_finais:
            if est_final in estados_acessiveis:
                finais_atualizados.append(est_final)
                
        self._estados_finais = finais_atualizados


    def eliminar_estados_equivalentes(self):
        """
        Aplica a minimização do autômato fundindo estados que possuem 
        as mesmas transições e o mesmo status de aceitação.
        """
        
        # Função auxiliar para manter os nomes dos estados planos
        # Ex: se vamos fundir (1, 2) com 3, vira (1, 2, 3) e não ((1, 2), 3)
        def normalizar_tupla(estado):
            return estado if isinstance(estado, tuple) else (estado,)

        while True:
            estados = list(self._tabela.keys())
            par_equivalente = None
            
            # 1 e 2. Busca por um par de estados equivalentes ("Gêmeos")
            for i in range(len(estados)):
                for j in range(i + 1, len(estados)):
                    e1 = estados[i]
                    e2 = estados[j]
                    
                    # Trava de segurança: Ambos devem ter o mesmo status de aceitação (final ou não)
                    eh_final_e1 = e1 in self._estados_finais
                    eh_final_e2 = e2 in self._estados_finais
                    
                    if eh_final_e1 == eh_final_e2:
                        # Como nosso autômato é determinístico, podemos comparar 
                        # as linhas inteiras do dicionário diretamente
                        if self._tabela[e1] == self._tabela[e2]:
                            par_equivalente = (e1, e2)
                            break # Encontrou um par! Interrompe a busca.
                
                if par_equivalente:
                    break
                    
            # CONDIÇÃO DE PARADA (Regra 4 - Recursividade): 
            # Se não achou nenhum par equivalente na varredura toda, o autômato está mínimo!
            if not par_equivalente:
                break 
                
            # --- 3. A FUSÃO DOS ESTADOS ---
            e1, e2 = par_equivalente
            
            # Cria o nome do novo superestado
            novo_estado = tuple(sorted(set(normalizar_tupla(e1) + normalizar_tupla(e2)), key=str))
            
            # A linha do novo estado será idêntica à linha dos antigos
            self._tabela[novo_estado] = self._tabela[e1].copy()
            
            # Deleta as linhas velhas
            del self._tabela[e1]
            del self._tabela[e2]
            
            # --- 4. ATUALIZAÇÃO E REDIRECIONAMENTO ---
            
            # Se um dos estados antigos era o inicial, o novo herda a coroa
            if str(self._estado_inicial) in (str(e1), str(e2)):
                self._estado_inicial = str(novo_estado)
                
            # Se eram finais, substituímos os velhos pelo novo na lista
            finais_temporarios = set(self._estados_finais)
            if e1 in finais_temporarios or e2 in finais_temporarios:
                finais_temporarios.discard(e1)
                finais_temporarios.discard(e2)
                finais_temporarios.add(novo_estado)
            self._estados_finais = list(finais_temporarios)
            
            # Regra 3 (O Redirecionamento Global): 
            # Vasculha a tabela e aponta todas as setas para o superestado
            for estado, transicoes in self._tabela.items():
                for simbolo, destinos in transicoes.items():
                    novos_destinos = []
                    for dest in destinos:
                        # Se o destino era e1 ou e2, agora aponta para o novo_estado
                        if dest == e1 or dest == e2:
                            if novo_estado not in novos_destinos:
                                novos_destinos.append(novo_estado)
                        else:
                            if dest not in novos_destinos:
                                novos_destinos.append(dest)
                                
                    self._tabela[estado][simbolo] = novos_destinos
            
            # O laço while True reiniciará agora, lendo a tabela com o estado já fundido,
            # cumprindo a exigência de recursividade perfeitamente.