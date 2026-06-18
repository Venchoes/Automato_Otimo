import os
import copy

from models.AutomatoBruto import AutomatoBrutoClass as AB
from models.AutomatoOtimo import AutomatoOtimoClass as AO

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

def controleAutomatoBruto(t: AB, destino: str):

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

    # 1. Gera os dados em memória (Dicionário)
    t.gerarDicionarioBruto()

    # 2. Formata para visualização
    print("--- Tabela de Transições (Bruta) ---")
    tabela_visual, tabela_numpy = t.formatarTabela()

    t.exportarCSV(os.path.join(destino, "1_bruto.csv"), tabela_numpy)

def controleAutomatoOtimo(bruto: AB, pasta_saida: str):
    print("\n" + "="*50)
    print("INICIANDO FASE DE OTIMIZAÇÃO")
    print("="*50)

    # Cria o autômato ótimo puxando a herança e os dados do bruto
    otimo = AO.fromBruto(bruto)

    print("\n--- Tabela Sem Transições em Vazio ---")
    otimo.eliminar_transicoes_vazio()
    visual_vazio, numpy_vazio = otimo.formatarTabela()
    #print(visual_vazio)
    otimo.exportarCSV(os.path.join(pasta_saida, "2_sem_vazio.csv"), numpy_vazio)

    print("\n--- Tabela Determinística ---")
    otimo.eliminar_transicoes_nao_deterministicas()
    visual_det, numpy_det = otimo.formatarTabela()
    #print(visual_det)
    otimo.exportarCSV(os.path.join(pasta_saida, "3_determinado.csv"), numpy_det)

    print("\n--- Tabela Sem Estados Não Acessíveis ---")
    otimo.eliminar_estados_nao_acessiveis()
    visual_acess, numpy_acess = otimo.formatarTabela()
    #print(visual_acess)
    otimo.exportarCSV(os.path.join(pasta_saida, "4_acessiveis.csv"), numpy_acess)

    print("\n--- Autômato Mínimo (Final) ---")
    otimo.eliminar_estados_equivalentes()
    visual_minimo, numpy_minimo = otimo.formatarTabela()
    #print(visual_minimo)
    otimo.exportarCSV(os.path.join(pasta_saida, "5_minimo.csv"), numpy_minimo)


if __name__ == "__main__":

    pasta = "wirth"
    wirths = ler_arquivos_wirth(pasta)
    
    if not wirths:
        print("Nenhum arquivo válido encontrado para processamento.")
    else:
        for nome, conteudo_wirth in wirths:

            nome_base = nome.replace('.txt', '')
            pasta_saida = os.path.join("output", nome_base)
            os.makedirs(pasta_saida, exist_ok=True)

            # Fluxo Bruto
            t = AB(conteudo_wirth)
            controleAutomatoBruto(t, pasta_saida)
            
            # Fluxo Ótimo
            controleAutomatoOtimo(t, pasta_saida)