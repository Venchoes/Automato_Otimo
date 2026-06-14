import os
import numpy as np
import csv

from models.AutomatoBruto import AutomatoBrutoClass as AB

def ler_arquivos_wirth(pasta_destino: str) -> list:
    """Lê todos os arquivos .txt do diretório especificado e retorna uma lista de tuplas (nome_arquivo, conteudo)"""
    wirths = []
    
    # Verifica se a pasta existe antes de tentar ler
    if not os.path.exists(pasta_destino):
        print(f"Aviso: A pasta '{pasta_destino}' não foi encontrada.")
        return wirths

    # Varre a pasta, filtra os txt e faz a leitura
    for nome_arquivo in sorted(os.listdir(pasta_destino)):
        if nome_arquivo.endswith(".txt"):
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            with open(caminho_completo, 'r', encoding='utf-8') as arquivo:
                conteudo = arquivo.read().strip()
                if conteudo:
                    wirths.append((nome_arquivo, conteudo))
                    
    return wirths

def printAutomatoBruto(conteudo: str):

    t = AB(conteudo)
    print("--- Posições ---")
    print(t.atribuirPosicao())
    print("\n--- Regras de Estado ---")
    print(t.regrasEstado() + "\n")

    print("--- Transições ---")
    print(t.determinarTransicoes())
    print("\n--- Estados (Inicial e Finais) ---")
    estado_inicial, estados_finais = t.determinarEstados()
    print(f"Inicial: {estado_inicial}")
    print(f"Finais: {estados_finais}\n")

    print("--- Tabela de Transições ---")
    tabela_visual, tabela_numpy = t.montarTabelaTransicoes()
    print(tabela_visual)

    nome_exportacao = f"output/tabela_{nome.replace('.txt', '')}.csv"
    with open(nome_exportacao, mode='w', newline='', encoding='utf-8') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv, delimiter=';') # Usando ponto-e-vírgula para evitar conflito com as vírgulas das listas
            
            # O tabela_numpy já tem o cabeçalho na primeira linha e os dados nas demais
            for linha in tabela_numpy:
                escritor_csv.writerow(linha)
    print(f"\n[!] Tabela exportada com sucesso para '{nome_exportacao}'\n")


if __name__ == "__main__":

    pasta = "wirth"
    wirths = ler_arquivos_wirth(pasta)
    
    if not wirths:
        print("Nenhum arquivo válido encontrado para processamento.")
    
    for nome, conteudo_wirth in wirths:
        printAutomatoBruto(conteudo_wirth)
        