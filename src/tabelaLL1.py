from collections import defaultdict

# Classe para armazenar a tabela de análise LL(1)
class TableLL1:
    def __init__(self, filename, start_symbol):
        # Guarda do símbolo inicial
        self.start_symbol = start_symbol

        # Pega a gramática LL(1) pelo arquivo passado
        grammar = self.LL1PeloArquivo(filename)

        # Guarda todos os não terminais e terminais da grámatica
        self.nts, self.ts = self.NaoTerminais(grammar), self.Terminais(grammar)

        # Gera os conjuntos First da gramática
        first_sets = self.ConjuntosFirst(grammar)

        # Gera os conjuntos Follow da gramática
        follow_sets = self.ConjuntosFollow(grammar, start_symbol, first_sets)

        # Gera e armazena a tabela de análise
        self.parsing_table = self.GerarTabelaLL1(grammar, first_sets, follow_sets)

    # Carrega a gramática a partir de um arquivo, retornando um dicionário onde as chaves 
    # são os não terminais e os valores são listas de produções.
    def LL1PeloArquivo(self, filename):
        grammar = defaultdict(list)
        try:
            # Abre o arquivo da gramática
            with open(filename, 'r', encoding='utf-8') as file:
                # Lê o o arquivo linha por linha
                for line in file:
                    line = line.strip()
                    # Se não tiver nada na linha pula
                    if not line:
                        continue
                    # Se não tiver -> na linha, a linha é ínvalida pois todas as linhas precisam ter uma derivação
                    if '->' not in line:
                        print(f"Skipping invalid line: {line}")
                        continue
                    # lhs recebe o não terminal e rhs recebe as produções de lhs
                    lhs, rhs = line.split('->', 1)
                    lhs = lhs.strip()
                    # Separa as produções de rhs
                    productions = [prod.strip() for prod in rhs.split('|')]
                    # EXPR_OU2 -> || EXPR_E EXPR_OU2 | ε
                    # Como está produção usa dois | (||) como terminal temos que tratar está produção para ela funcionar 
                    for prod in range(len(productions)):
                        if productions[prod] == "" and productions[prod+1] == "":
                            productions = productions[2:]
                            productions[0] = '|| ' + productions[0]
                            break
                    # Adiona a chave lhs e as produções na gramática
                    grammar[lhs].extend(productions)
        except FileNotFoundError:
            print(f"Erro: O arquivo {filename} não foi encontrado.")
            return {}
        except IOError as e:
            print(f"Erro ao ler o arquivo {filename}: {e}")
            return {}
        
        # Retorna a gramática no arquivo 
        return dict(grammar)

    # Retorna um conjunto com todos os símbolos não terminais
    def NaoTerminais(self, grammar):
        return set(grammar.keys())

    # Retorna um conjunto com todos os símbolos terminais
    def Terminais(self, grammar):
        # Pega todos os não terminais
        non_terminals = self.NaoTerminais(grammar)
        terminals = set()
        # Para cada lista de produções na gramática
        for rhs_list in grammar.values():
            # Para cada produção na lista
            for production in rhs_list:
                # Separa os símbolos
                symbols = production.split()
                # Para cada símbolo
                for symbol in symbols:
                    # Se símbolo for dirente de ε e não é um não terminal
                    if symbol != 'ε' and symbol not in non_terminals:
                        # Adiciona no conjunto de terminais
                        terminals.add(symbol)
        return terminals

    # Metódo para gerar todos os conjuntos First
    def ConjuntosFirst(self, grammar):
        # Gera todos os conjuntos FIRST como vazios para todos não terminais da gramática
        first_sets = {non_terminal: set() for non_terminal in self.nts}

        # Função recursiva interna para fazer a busca recursiva do First de um símbolo
        def EncontrarFirstSet(symbol):
            # Se o conjunto First de symbol já existe retorna ele        
            if first_sets[symbol]:
                return first_sets[symbol]
            
            # Para cada produção de symbol na grámatica faça
            for production in grammar[symbol]:
                # Pega todos símbolos da produção
                p_symbols = production.split()
                # Variável auxiliar para saber se um não terminal possui ε apenas se todos os seus símbolos produzem ε
                all_empty = True

                # Para cada símbolo nos símbolos da produção
                for p_symbol in p_symbols:
                    # Se o símbolo for ε, adiciona ε ao First de symbol e sai do for
                    if p_symbol == 'ε':
                        first_sets[symbol].add('ε')
                        all_empty = False
                        break
                    # Se o símbolo é um terminal, adiciona o símbolo ao First de symbol e sai do for
                    elif p_symbol in self.ts:
                        first_sets[symbol].add(p_symbol)
                        all_empty = False
                        break
                    # Se o símbolo é um não terminal
                    else:
                        # Encontra o First do símbolo
                        first_p_symbol = EncontrarFirstSet(p_symbol)
                        # Adiciona ao First do symbol o First do símbolo tirando o ε
                        first_sets[symbol].update(first_p_symbol - {'ε'})
                        # Se o ε não estiver no First do símbolo sai do for, senão continua o for
                        if 'ε' not in first_p_symbol:
                            all_empty = False
                            break
                # Se todos os símbolos da produção produzem ε adiciona ε ao First de symbol
                if all_empty:
                    first_sets[symbol].add('ε')
            # Retorna o First de symbol            
            return first_sets[symbol]

        # Para todos os não terminais gera os conjuntos First
        for non_terminal in self.nts:
            EncontrarFirstSet(non_terminal)

        # Retorna todos os conjuntos First 
        return first_sets
    
    # Metódo para gerar todos os conjuntos FOllow
    def ConjuntosFollow(self, grammar, start_symbol, first_sets):
        # Inicializa para todos não teminais o conjunto Follow como vazio 
        follow = defaultdict(set)
        
        # Adiciona o $ para o conjunto Follow do símbolo inicial
        follow[start_symbol].add('$')

        # Função recursiva interna para fazer a busca recursiva do Follow de um símbolo
        def follow_of(symbol):
            # Certifica que o símbolo tem um conjunto Follow
            if symbol not in follow:
                follow[symbol] = set()

            # Para cada não terminal na gramática
            for nt in self.nts:
                # Para cada produção do não terminal
                for production in grammar[nt]:
                    # Separa os símbolos da produção
                    symbols = production.split()
                    
                    # Conferi se o símbolo atual está na produção do não terminal
                    if symbol in symbols:
                        # Começa a verificar os símbolos após o símbolo atual
                        follow_pos = symbols.index(symbol) + 1
                        
                        # Enquanto o símbolo checado não depois  do último
                        while follow_pos < len(symbols):
                            # Guarda o próximo símbolo
                            next_symbol = symbols[follow_pos]
                            
                            # Se o próximo símbolo for um não terminal
                            if next_symbol in self.nts:
                                # Adiciona o First do próximo símbolo no Follow do símbolo atual, excluindo o ε
                                follow[symbol] |= first_sets[next_symbol] - {'ε'}
                                
                                # Se o First do próximo símbolo não contém o ε, sai do loop
                                if 'ε' not in first_sets[next_symbol]:
                                    break
                            # Se o próximo símbolo é um terminal
                            else:
                                # Adiciona o terminal ao Follow do símbolo atual
                                follow[symbol].add(next_symbol)
                                # Sai do loop
                                break
                            
                            # Vai para o próximo símbolo da produção
                            follow_pos += 1
                        
                        # Se chegou ao final da produção ou todos os símbolos restantes derivão em ε
                        if follow_pos == len(symbols):
                            # Evita dependências própias (não adicionar o conjunto Follow do símbolo atual em si mesmo)
                            if nt != symbol:
                                # Adiciona o Follow do não terminal ao Follow do símbolo atual
                                follow[symbol] |= follow_of(nt)
            
            # Retorna o conjunto Follow do símbolo atual
            return follow[symbol]

        # Para todos os não terminais gera os conjuntos Follow
        for non_terminal in grammar:
            follow_of(non_terminal)

        # Retorna todos os conjuntos Follow
        return dict(follow)

    # Metódo para gerar a tabela de análise
    def GerarTabelaLL1(self, grammar, first_sets, follow_sets):
        # Constrói a tabela de análise LL(1) a partir da gramática, dos conjuntos FIRST e FOLLOW

        # Adiciona o marcador de fim de entrada aos terminais
        terminals = self.ts | {'$'}
        non_terminals = self.nts

        # Começa a tabela com todas posições valendo '-'
        parsing_table = {nt: {t: '-' for t in terminals} for nt in non_terminals}

        # Para cada não teminal
        for non_terminal in grammar.keys():
            # Para cada terminal do cojunto First do não terminal
            for terminal_first in first_sets[non_terminal]:
                # Se o terminal for diferente de ε
                if terminal_first != 'ε':
                    # Para cada produção do não terminal na gramática
                    for production in grammar[non_terminal]:
                        # Separa os símbolos da produção
                        symbols = production.split()
                        # Para cada símbolo
                        for symbol in symbols:
                            # Se o símbolo for diferente de ε
                            if symbol != 'ε':
                                # Se o símbolo for um terminal
                                if symbol in terminals:
                                    # Se o símbolo é o terminal do conjunto First sendo analisado
                                    if terminal_first == symbol:
                                        # Adiciona a produção na table na posição linha do não terminal e coluna do terminal do conjunto First sendo analisado 
                                        parsing_table[non_terminal][terminal_first] = production
                                # Se o símbolo é um não terminal
                                # Verifica se o terminal do conjunto First está no conjunto First do símbolo
                                elif terminal_first in first_sets[symbol]:
                                    # Adiciona a produção na table na posição linha do não terminal e coluna do terminal do conjunto First sendo analisado 
                                    parsing_table[non_terminal][terminal_first] = production
                                # Se o conjunto First do símbolo possui o ε continua o loop dos símbolos
                                elif 'ε' in first_sets[symbol]:
                                    continue
                                # Se não possui ε sai do loop de símbolos
                                break
                # Se o terminal for ε
                else:
                    # Para cada terminal do conjunto Follow do não terminal
                    for terminal in follow_sets[non_terminal]:
                        # Adiciona a produção ε na table na posição linha do não terminal e coluna do terminal do conjunto Follow sendo analisado
                        parsing_table[non_terminal][terminal] = 'ε'
        return parsing_table

    # Função para retorna a derivação de um símblo para um símbolo da entrada
    def RetornarDerivacao(self, symbol, input):
        return self.parsing_table[symbol][input]