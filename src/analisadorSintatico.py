import tabelaLL1 as ll1

class Sintatico:
    def __init__(self, grammar, start):
        # Inicializa o analisador sintático, carregando a tabela LL(1) da gramática especificada
        self.ll1 = ll1.TableLL1(grammar, start)

    # Método principal do analisador léxico, testa se a lista de tokens está sintaicamente correta
    def testaTokens(self, tokens):
        # Cria uma cópia da lista de tokens e adiciona o marcador de fim da entrada ('$')
        input_data = tokens.tokens.copy()
        input_data.append(('$', ''))
        
        # Inicializa a pilha de símbolos com o símbolo inicial da gramática
        stack = list()
        stack.append(self.ll1.start_symbol)
        
        # Loop principal do analisador sintático
        while True:
            # Obtém o primeiro símbolo da entrada, convertendo para minúsculas
            first_symbol = input_data[0][0].lower()

             # Verifica se a pilha está vazia e a entrada foi totalmente consumida
            if not stack and first_symbol == '$':
                # Se sim, o código está sintaticamente correto
                print('Código sintaticamente correto!')
                return
            else:
                # Pega o símbolo no topo da pilha
                symbol = stack.pop()
                # Se o topo da pilha é um terminal e não coincide com o símbolo de entrada
                if symbol in self.ll1.ts and symbol != first_symbol:
                    print('Código sintaticamente incorreto')
                    print('Erro ao comparar o topo da pilha com a entrada!')
                    return
                # Se o símbolo não coincide com o primeiro símbolo da entrada
                elif symbol != first_symbol:
                    # Obtém a derivação correspondente na tabela LL(1)
                    derivate = self.ll1.RetornarDerivacao(symbol, first_symbol).split()
                    # Reverte a derivação para inserção correta na pilha
                    derivate = derivate[::-1]

                    # Para cada símbolo na derivação
                    for s in derivate:
                        # Se s for -, não há a derivação na tabela
                        if s == '-':
                            print('Código sintaticamente incorreto')
                            print(f'Não existe derivação para {symbol} com {first_symbol}!')
                            return
                        # Se o símbolo não é ε, empilha ele
                        elif s != 'ε':
                            stack.append(s)
                # Se o símbolo do topo da pilha coincide com o símbolo da entrada, consome o símbolo da entrada
                else:
                    input_data.pop(0)
