import re
import numpy as np


class AutomatoOtimoClass(object):
    
	def __init__(self, prod_gramaticais: str) -> None:
		self.__prod_gramaticais = prod_gramaticais.strip()
		self.__tokens = self.__tokenizar(self.__prod_gramaticais)
		self.__variavel = self.__tokens[: self.__tokens.index("=") + 1] if "=" in self.__tokens else []

		self.__transicoes: list[tuple[int, str, int]] = []
		self.__estado_inicial = "0"
		self.__estados_finais: list[int] = []
		self.__proximo_estado = 0
		self.__construido = False

	def __tokenizar(self, texto: str) -> list[str]:
		padrao_regex = r'"[^"]*"|\w+|=|\||\{|\}|\(|\)|\[|\]'
		return re.findall(padrao_regex, texto)

	def __novo_estado(self) -> int:
		estado = self.__proximo_estado
		self.__proximo_estado += 1
		return estado

	def __adicionar_transicao(self, origem: int, simbolo: str, destino: int) -> None:
		transicao = (origem, simbolo, destino)
		if transicao not in self.__transicoes:
			self.__transicoes.append(transicao)

	def __eh_simbolo_terminal(self, token: str) -> bool:
		return token not in {"=", "|", "(", ")", "[", "]", "{", "}"}

	def __montar_fragmento_simbolo(self, simbolo: str) -> tuple[int, int]:
		origem = self.__novo_estado()
		destino = self.__novo_estado()
		self.__adicionar_transicao(origem, simbolo, destino)
		return origem, destino

	def __montar_concat(self, esquerda: tuple[int, int], direita: tuple[int, int]) -> tuple[int, int]:
		self.__adicionar_transicao(esquerda[1], "e", direita[0])
		return esquerda[0], direita[1]

	def __montar_alternancia(self, opcoes: list[tuple[int, int]]) -> tuple[int, int]:
		inicio = self.__novo_estado()
		fim = self.__novo_estado()

		for origem, destino in opcoes:
			self.__adicionar_transicao(inicio, "e", origem)
			self.__adicionar_transicao(destino, "e", fim)

		return inicio, fim

	def __montar_opcional(self, fragmento: tuple[int, int]) -> tuple[int, int]:
		inicio = self.__novo_estado()
		fim = self.__novo_estado()
		self.__adicionar_transicao(inicio, "e", fragmento[0])
		self.__adicionar_transicao(inicio, "e", fim)
		self.__adicionar_transicao(fragmento[1], "e", fim)
		return inicio, fim

	def __montar_repeticao(self, fragmento: tuple[int, int]) -> tuple[int, int]:
		inicio = self.__novo_estado()
		fim = self.__novo_estado()
		self.__adicionar_transicao(inicio, "e", fragmento[0])
		self.__adicionar_transicao(inicio, "e", fim)
		self.__adicionar_transicao(fragmento[1], "e", fragmento[0])
		self.__adicionar_transicao(fragmento[1], "e", fim)
		return inicio, fim

	def __ler_bloco(self, inicio: int, fechamento: str | None = None) -> tuple[tuple[int, int], int]:
		fragmentos: list[tuple[int, int]] = []
		i = inicio

		while i < len(self.__tokens):
			token = self.__tokens[i]

			if fechamento is not None and token == fechamento:
				break

			if token == "|":
				i += 1
				continue

			if token == "(":
				subfrag, novo_i = self.__ler_alternativas(i + 1, ")")
				fragmentos.append(subfrag)
				i = novo_i + 1
				continue

			if token == "[":
				subfrag, novo_i = self.__ler_alternativas(i + 1, "]")
				fragmentos.append(self.__montar_opcional(subfrag))
				i = novo_i + 1
				continue

			if token == "{":
				subfrag, novo_i = self.__ler_alternativas(i + 1, "}")
				fragmentos.append(self.__montar_repeticao(subfrag))
				i = novo_i + 1
				continue

			if self.__eh_simbolo_terminal(token):
				fragmentos.append(self.__montar_fragmento_simbolo(token))
				i += 1
				continue

			i += 1

		if not fragmentos:
			vazio = self.__novo_estado(), self.__novo_estado()
			self.__adicionar_transicao(vazio[0], "e", vazio[1])
			return vazio, i

		resultado = fragmentos[0]
		for fragmento in fragmentos[1:]:
			resultado = self.__montar_concat(resultado, fragmento)

		return resultado, i

	def __ler_alternativas(self, inicio: int, fechamento: str) -> tuple[tuple[int, int], int]:
		opcoes: list[tuple[int, int]] = []
		i = inicio

		while i < len(self.__tokens):
			token = self.__tokens[i]
			if token == fechamento:
				break

			fragmento, novo_i = self.__ler_bloco(i, fechamento)
			opcoes.append(fragmento)
			i = novo_i

			if i < len(self.__tokens) and self.__tokens[i] == "|":
				i += 1

		if len(opcoes) == 1:
			return opcoes[0], i

		return self.__montar_alternancia(opcoes), i

	def __construir(self) -> None:
		if self.__construido:
			return

		if "=" not in self.__tokens:
			raise ValueError("Entrada Wirth inválida: símbolo '=' não encontrado.")

		inicio_corpo = self.__tokens.index("=") + 1
		fragmento_final, _ = self.__ler_bloco(inicio_corpo)

		self.__estado_inicial = str(fragmento_final[0])
		self.__estados_finais = [fragmento_final[1]]
		self.__construido = True

	def __getProducao(self, tokens: list, index: int) -> list:
		return tokens[(index + 1):]

	def __getStringVariavel(self) -> str:
		return " ".join(str(var) for var in self.__variavel)

	def atribuirPosicao(self) -> str:
		return self.__prod_gramaticais

	def regrasEstado(self) -> str:
		self.__construir()
		return f"{self.__getStringVariavel()}{self.__transicoes}"

	def determinarTransicoes(self) -> str:
		self.__construir()
		return "\n".join(str(trans) for trans in self.__transicoes)

	def __determinarEstadoInicial(self) -> str:
		self.__construir()
		return self.__estado_inicial

	def __determinarEstadosFinais(self) -> str:
		self.__construir()
		return str(self.__estados_finais)

	def determinarEstados(self) -> tuple[str, list]:
		self.__construir()
		return self.__estado_inicial, self.__estados_finais

	def montarTabelaTransicoes(self) -> tuple[str, np.ndarray]:
		self.__construir()

		estados = set()
		alfabeto = set()

		for origem, simbolo, destino in self.__transicoes:
			estados.add(origem)
			estados.add(destino)
			if simbolo != "e":
				alfabeto.add(simbolo)

		if not estados:
			estados.add(0)

		lista_estados = sorted(estados)
		lista_alfabeto = sorted(alfabeto) + ["e"]
		matriz_transicao = {estado: {simbolo: [] for simbolo in lista_alfabeto} for estado in lista_estados}

		for origem, simbolo, destino in self.__transicoes:
			if destino not in matriz_transicao[origem][simbolo]:
				matriz_transicao[origem][simbolo].append(destino)

		cabecalho = ["Estado"] + lista_alfabeto
		linhas_tabela = [" | ".join(f"{col:^10}" for col in cabecalho)]
		linhas_tabela.append("-" * len(linhas_tabela[0]))
		matriz_np = [cabecalho]

		for estado in lista_estados:
			prefixo = ""
			if str(estado) == self.__estado_inicial:
				prefixo += "->"
			if estado in self.__estados_finais:
				prefixo += "*"

			estado_formatado = f"{prefixo}{estado}"
			linha_txt = [f"{estado_formatado:<10}"]
			linha_np = [estado_formatado]

			for simbolo in lista_alfabeto:
				celula_destinos = matriz_transicao[estado][simbolo]
				celula_str = str(sorted(celula_destinos)) if celula_destinos else "[]"
				linha_txt.append(f"{celula_str:^10}")
				linha_np.append(celula_str)

			linhas_tabela.append(" | ".join(linha_txt))
			matriz_np.append(linha_np)

		return "\n".join(linhas_tabela), np.array(matriz_np, dtype=object)


AutomatoOtimo = AutomatoOtimoClass