################################################################################
#                                IME-USP (2017)                                #
#                    MAC0422 - Sistemas Operacionais - EP3                     #
#                                                                              #
#                                   Processo                                   #
#                                                                              #
#                              Raphael R. Gusmao                               #
################################################################################

import math
from ep3 import Color
from memory import Memory

################################################################################
# Processo
class Process (object):
    ############################################################################
    # Construtor
    def __init__ (self, pid, line, memo):
        self.pid  = pid # Identificador do processo
        self.t0   = int(line[0]) # Momento que o processo chega no sistema
        self.tf   = int(line[1]) # Momento que o processo eh finalizado
        self.b    = int(line[2]) # Quantidade de memoria utilizada pelo processo
        self.name = line[3] # Nome do processo
        # Acessos a memoria feitos pelo processo: (momento, posicao)
        self.accesses = [(int(line[i+1]), int(line[i])) for i in range(4, len(line), 2)]
        self.accesses.sort() # Ordena por momento de acesso
        self.memo = memo # Gerenciador de memoria

    ############################################################################
    # Inicia o processo
    def begin (self, memo):
        # Quantidade minima de memoria que o processo precisa levando  em  conta
        # o tamanho da unidade de alocacao
        self.b = math.ceil(self.b/self.memo.s)*self.memo.s
        if (self.memo.debug):
            print(Color.GREEN + "* Processo \"" + self.name + "\" (PID: " + str(self.pid) + ") (b: " + str(self.b) + ") chegou" + Color.END)
        self.memo.allocate(self)

    ############################################################################
    # Acessa uma posicao da memoria
    def memory_access (self, memo):
        position = self.accesses[0][1]
        del self.accesses[0]
        if (self.memo.debug):
            print(Color.YELLOW + "* Processo \"" + self.name + "\" (PID: " + str(self.pid) + ") acessou a posicao " + str(position) + Color.END)
        # Parte do espaco reservado ao processo em que a posicao esta
        # (cada parte tem o tamanho de uma pagina)
        part = int(position/self.memo.p)
        self.memo.access(self, part)

    ############################################################################
    # Finaliza o processo
    def finish (self, memo):
        if (self.memo.debug):
            print(Color.PINK + "* Processo \"" + self.name + "\" (PID: " + str(self.pid) + ") finalizou" + Color.END)
        self.memo.deallocate(self)
        self.memo.remove_pages_from_process(self)

################################################################################
