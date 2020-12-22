################################################################################
#                                IME-USP (2017)                                #
#                    MAC0422 - Sistemas Operacionais - EP3                     #
#                                                                              #
#                                  Simulador                                   #
#                                                                              #
#                              Raphael R. Gusmao                               #
################################################################################

import time
import ep3
from ep3 import Color
from memory import Memory
from process import Process

s_filename = None # Arquivo de trace
again = False # Indica se o mesmo trace vai ser executado novamente em seguida
memo = None # Gerenciador de memoria
processes = [] # Guarda os processos
times_to_compact_memory = [] # Guarda os momentos que a memoria deve ser compactada
n_processes = 0 # Numero de processos
n_accesses = 0 # Numero total de acessos a memoria fisica
page_faults = 0 # Numero de falhas de paginas ocorridas na simulacao
mean_time_fit = 0 # Tempo medio para encontrar um espaco livre na memoria virtual
elapsed_time = 0 # Tempo de execucao da simulacao

################################################################################
# Converte milissegundos para o formato "...h --m --s ---ms"
def format_time (cur_time):
    cur_time *= 1000
    ms = cur_time % 1000
    s  = int(cur_time / 1000) % 60
    m  = int(cur_time / (1000*60)) % 60
    h  = int(cur_time / (1000*60*60)) % 24
    return (str(h)+"h " + str(m)+"m " + str(s)+"s " + str(int(ms))+"ms")

################################################################################
# Carrega o arquivo de trace filename
def load_file (filename):
    global s_filename, again, memo, processes, times_to_compact_memory, n_processes, n_accesses
    s_filename = filename
    again = False
    processes = []
    times_to_compact_memory = []
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines()]
    memo = Memory(lines[0].split())
    n_accesses = 0
    pid = 0
    for line in lines[1:]:
        line = line.split()
        if (len(line) == 2): # COMPACTA
            times_to_compact_memory.append(int(line[0]))
        else: # Processo
            new_process = Process(pid, line, memo)
            processes.append(new_process)
            n_accesses += len(new_process.accesses)
            pid = (pid + 1) % 128 # Cada pid tem 8 bits
    times_to_compact_memory.sort()
    n_processes = len(processes)
    return True

################################################################################
# Executa a simulacao
def simulate (id_fit, id_sub, interval, debug):
    global again, page_faults, mean_time_fit, elapsed_time
    # Se o mesmo trace for executado novamente em seguida
    if (again):
        load_file(s_filename) # Recarrega os dados do arquivo de trace
    again = True

    # Descricao da simulacao
    print(Color.BLUE + "\nGerencia de espaco livre: " + Color.CYAN + str(ep3.fit[id_fit]) + Color.END)
    print(Color.BLUE + "Substituicao de pagina: " + Color.CYAN + str(ep3.sub[id_sub]) + Color.END)

    # Inicio da simulacao
    print(Color.BLUE + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Inicio da simulacao ]" + Color.END)
    start_time = time.time()

    # Define os algoritmos que serao utilizados
    memo.set_algorithms(id_fit, id_sub, processes)
    memo.debug = debug

    # Exibe o estado inicial da memoria
    if (interval > 0):
        memo.show()

    # Cada loop eh 1 segundo
    cur_time = -1
    while (True):
        cur_time += 1
        if (memo.debug or (interval > 0 and cur_time % interval == 0)):
            print(Color.BLUE + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Tempo: " + str(cur_time) + " ]\n" + Color.END)

        # Atualiza o bit R
        memo.update_R_bit()

        # Compactacao de memoria
        while (len(times_to_compact_memory) > 0 and cur_time == times_to_compact_memory[0]):
            memo.compact()
            del times_to_compact_memory[0]

        # Chegada de processos
        for process in processes:
            if (process.t0 == cur_time):
                process.begin(memo)

        # Acessos a memoria
        for process in processes:
            while (len(process.accesses) > 0 and cur_time == process.accesses[0][0]):
                process.memory_access(memo)

        # Saida de processos
        to_remove = []
        for process in processes:
            if (process.tf == cur_time):
                process.finish(memo)
                to_remove.append(process)
        for process in to_remove:
            processes.remove(process)

        # Exibe a memoria na tela
        if (interval > 0 and cur_time % interval == 0):
            memo.show()

        # Finaliza o simulador quando todos os processos forem finalizados
        if (len(processes) == 0):
            break

    # Fim da simulacao
    print(Color.BLUE + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Fim da simulacao ]" + Color.END)
    end_time = time.time()
    memo.close_memory_files()

    # Relatorio da simulacao
    mean_time_fit = memo.allocate_time/n_processes
    elapsed_time = end_time - start_time
    page_faults = memo.page_faults
    ratio = 100*page_faults/n_accesses
    print(Color.BLUE + "Processos: " + Color.CYAN + str(n_processes) + Color.END)
    print(Color.BLUE + "Acessos a memoria fisica: " + Color.CYAN + str(n_accesses) + Color.END)
    print(Color.BLUE + "Page Faults: " + Color.CYAN + str(page_faults) + Color.BLUE + " ({0:.2f}%)".format(ratio) + Color.END)
    print(Color.BLUE + "Tempo simulado: " + Color.CYAN + str(cur_time) + " s " + Color.END)
    print(Color.BLUE + "Tempo medio para encontrar espaco livre: " + Color.CYAN + str(mean_time_fit)+" s" + Color.END)
    print(Color.BLUE + "Tempo total de execucao: " + Color.CYAN + str(elapsed_time)+" s" + Color.BLUE + " (" + format_time(elapsed_time) + ")\n" + Color.END)

################################################################################
