# ⚙️ Gerador de Autômato Bruto (Simplificação Wirth para AFN)

Este projeto implementa um compilador/transpilador léxico que converte regras gramaticais simplificadas em notação de Wirth para um Autômato Finito Não-Determinístico (AFN) bruto. 

O sistema processa as gramáticas, atribui estados, calcula transições (incluindo transições em vazio/épsilon) e exporta a **Tabela de Transição de Estados** pronta para visualização, análise e documentação.

---

## 📁 Estrutura do Projeto

O projeto é estruturado da seguinte forma:

```text
📦 raiz_do_projeto
 ┣ 📂 models/
 ┃ ┗ 📜 AutomatoBruto.py   # Classe principal com a lógica do AFN
 ┣ 📂 wirth/               # Pasta de entrada (Inputs)
 ┃ ┣ 📜 1.txt              # Arquivo contendo a regra Wirth (ex: variavel = "a" | "b" .)
 ┃ ┗ 📜 ... 
 ┣ 📂 output/              # Pasta de saída (Outputs gerados)
 ┃ ┣ 📜 tabela_1.csv       # Tabela exportada em CSV
 ┃ ┗ 📜 tabela_1.npy       # Matriz exportada em formato NumPy nativo
 ┗ 📜 main.py              # Script principal de execução em lote
```
---

## 🧠 Comportamento da Classe `AutomatoBrutoClass`

A classe `AutomatoBrutoClass` encapsula toda a complexidade da conversão da gramática. O processamento é dividido em 5 etapas estritas, baseadas nas regras de construção de autômatos:

1. **`atribuirPosicao()`:**
* Analisa a string de entrada via Expressões Regulares (Regex).
* Isola a variável principal e insere delimitadores de posição (`.`) entre cada token terminal, não-terminal e símbolos de agrupamento.

2. **`regrasEstado()`:**
* Percorre a cadeia de posições determinando a numeração dos estados.
* Regra 1: Atribui o estado `0` no início.
* Regra 2 & 3: Utiliza uma estrutura de **Pilha** para propagar estados ao redor de parênteses `()`, colchetes `[]` (opcionais) e chaves `{}` (repetições).
* Regra 4: Para átomos normais, consome o token e incrementa o estado (`j+1`).

3. **`determinarTransicoes()`:**
* Mapeia as mudanças de um estado de origem para um estado de destino através do consumo de um átomo.
* Resolve agrupamentos mapeando **transições em vazio (`e`)** do final da estrutura de volta para o início (repetição) ou pulando a estrutura inteira (opcionalidade).

4. **`determinarEstados()`:**
* **Estado Inicial ($q_0$):** Fixo no estado `0`.
* **Estados Finais ($F$):** Identifica os estados localizados imediatamente antes de operadores de alternância (`|`) no nível raiz (fora de agrupamentos) e o último estado absoluto da cadeia.

5. **`montarTabelaTransicoes()`:**
* Cruza a lista de Estados ($Q$) gerados com o Alfabeto ($\Sigma$).
* Retorna uma representação textual perfeitamente tabulada para o terminal e uma matriz do NumPy.


---

## 🚀 Fluxo de Execução e Pasta `output`

O arquivo `main.py` foi projetado para ler múltiplos arquivos de gramática em lote. O funcionamento se dá pelo seguinte fluxo:

1. **Leitura (Input):** O script varre a pasta `wirth/` em busca de arquivos `.txt`. Cada arquivo representa uma gramática distinta.
2. **Processamento:** Para cada arquivo, o texto é instanciado na `AutomatoBrutoClass`, rodando todas as etapas passo a passo.
3. **Log em Tela:** O console exibe o passo a passo de forma didática: posições, regras de estado, transições, identificação do $q_0$ e $F$, além do rascunho visual da tabela.
4. **Exportação (Output):** O código gera automaticamente os arquivos finais e os salva na pasta `output/` (ou diretório equivalente configurado no main):
* **Arquivo `.npy`:** Salva a matriz 2D em formato binário otimizado para o Python (`numpy`).
* **Arquivo `.csv`:** Salva a tabela delimitada por ponto-e-vírgula (`;`).


### 💡 Dica: Levando os dados para o Google Docs/Planilhas

O formato `.csv` gerado lida perfeitamente com a notação de listas (ex: `[1, 2]`) típicas de um Autômato Não-Determinístico (AFN).
Para visualizar de forma elegante ou anexar a um relatório:

1. Abra o **Google Sheets**.
2. Vá em *Arquivo > Importar > Fazer Upload* e selecione o arquivo `.csv` gerado na pasta de output.
3. Marque o separador como **Personalizado** e digite `;` (ponto-e-vírgula).
4. Copie as células montadas e cole no seu **Google Docs** utilizando a opção "Colar desvinculado".

---

## ⚙️ Como Executar

Certifique-se de ter o Python 3 instalado, bem como a biblioteca NumPy.

1. Instale as dependências necessárias:

```bash
pip install numpy

```

2. Adicione seus arquivos `.txt` contendo as regras de Wirth dentro da pasta `wirth/`.
3. Rode o script principal na raiz do projeto:

```bash
python main.py

```