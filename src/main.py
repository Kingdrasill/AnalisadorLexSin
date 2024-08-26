import analisadorLexico as lex  # Importa o módulo do analisador léxico como 'lex'
import analisadorSintatico as sin # Importa o módulo do analisador sintático como 'sin'

gramatica = input("Nome do arquivo da gramática: ")
simbolo_inical = input("Símbolo inical da grmática: ")

# Inicializa o AFD, a tabela de símbolos, a lista de tokens e o analisador sintático
afd = lex.AFD() 
simbolos = lex.Simbolos()
tokens = lex.Tokens()
sintatico = sin.Sintatico(gramatica, simbolo_inical)

# Abre o arquivo de código fonte
codigo = input("Nome do arquivo do codigo: ")
file = open(codigo, 'r')
lines = file.readlines()
linha = 0

# Loop para testar cada linha do código fonte
for line in lines:
    linha += 1  # Incrementa o contador de linhas
    resp = afd.testaLinha(simbolos, tokens, linha, line)  # Chama a função para testar a linha
    if resp == False:  # Se houver um erro léxico
        break  # Sai do loop

# Imprime a lista de tokens e a tabela de símbolos
print('Lista de Tokes')
print(tokens)
print('Tabela de Simbolos')
print(simbolos)

# Testa se a lista de tokens está sintaticamente correta
sintatico.testaTokens(tokens)