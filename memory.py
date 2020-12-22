################################################################################
#                                IME-USP (2017)                                #
#                    MAC0422 - Sistemas Operacionais - EP3                     #
#                                                                              #
#                                   Memoria                                    #
#                                                                              #
#                              Raphael R. Gusmao                               #
################################################################################

import time
import math
from ep3 import Color

################################################################################
# Memoria
class Memory (object):
    ############################################################################
    # Construtor
    def __init__ (self, line):
        self.total, self.virtual, self.s, self.p = [int(x) for x in line]
        self.debug = False # Modo debug
        self.root = Node(-1, 0, self.virtual, None) # Lista ligada (memoria virtual)
        self.id_fit = 0 # Algoritmo para gerencia de espaco livre
        self.id_sub = 0 # Algoritmo de substituicao de pagina
        self.allocate_time = 0 # Tempo total gasto para encontrar espacos livres
        self.page_faults = 0 # Numero de Page Faults
        self.n_pages = int(self.total/self.p) # Numero de paginas
        self.root_page = Page(self.n_pages-1, -1, 0, 0, None) # Lista ligada de paginas
        for i in range(self.n_pages-1): # Inicializa as paginas
            self.root_page = Page(self.n_pages-2-i, -1, 0, 0, self.root_page)

        # Lista dos espacos livres que comportam os tamanhos mais requisitados
        # Implementada como um dicionario
        self.quick_list = {} # (Usada apenas no algoritmo Quick Fit)
        self.quick_node = {} # Meio de acesso rapido ao node escolhido pelo Quick Fit

        self.pages_queue = [] # Fila de paginas (Usada apenas no algoritmo FIFO)

         # Matriz de paginas (Usada apenas no algoritmo LRU 2)
        self.pages_matrix = [[0]*self.n_pages for i in range(self.n_pages)]

        # Arquivos das memorias
        self.mem_file = open("/tmp/ep3.mem", "wb+")
        self.write(self.mem_file, -1, 0, self.total)
        self.vir_file = open("/tmp/ep3.vir", "wb+")
        self.write(self.vir_file, -1, 0, self.virtual)

    ############################################################################
    # Fecha os arquivos das memorias
    def close_memory_files (self):
        self.mem_file.close()
        self.vir_file.close()

    ############################################################################
    # Exibe as memorias
    def show (self):
        # Memoria Virtual
        print(Color.BLUE + "* Memoria Virtual" + Color.END)
        node = self.root
        count = -1
        while (node != None):
            for i in range(node.size):
                count += 1
                if (count > 0 and count % self.s == 0): # Separa cada unidade de alocacao
                    print("|", end="")
                if (count > 0 and count % 16 == 0): # Pula linha a cada 16 posicoes
                    print()
                if (node.pid == -1):
                    print(" -1", end=" ")
                else:
                    print(Color.CYAN + "{:>3}".format(node.pid) + Color.END, end=" ")
            node = node.next_node
        print("|")
        ############################################################################
        # Memoria fisica
        print(Color.BLUE + "* Memoria Fisica" + Color.END)
        page = self.root_page
        count = -1
        while (page != None):
            for i in range(self.p):
                count += 1
                if (count > 0 and count % self.p == 0): # Separa cada pagina
                    print("|", end="")
                if (count > 0 and count % 16 == 0): # Pula linha a cada 16 posicoes
                    print()
                if (i < page.b):
                    print(Color.CYAN + "{:>3}".format(page.pid) + Color.END, end=" ")
                else:
                    print(" -1", end=" ")
            page = page.next_page
        print("|")

    ############################################################################
    # Escreve pid nas posicoes [pos, pos+b[ do arquivo file
    def write (self, file, pid, pos, b):
        file.seek(pos)
        for i in range(b):
            file.write(pid.to_bytes(1, byteorder='big', signed=True))

    ############################################################################
    # Atualiza os arquivos das memorias (usado apos a compactacao das memorias)
    def update_memory_files (self):
        # Memoria Virtual
        node = self.root
        while (node != None):
            self.write(self.vir_file, node.pid, node.base, node.size)
            node = node.next_node
        # Memoria fisica
        page = self.root_page
        base = 0
        while (page != None):
            b = min(self.p, page.b)
            self.write(self.mem_file, page.pid, base, b) # Parte do processo
            self.write(self.mem_file, -1, base+b, self.p-b) # Resto da pagina
            base += self.p
            page = page.next_page

    ############################################################################
    # Define os algoritmos que serao utilizados e faz preparacoes se necessario
    def set_algorithms (self, id_fit, id_sub, processes):
        self.id_fit = id_fit
        self.id_sub = id_sub
        if (self.id_fit == 3): # Quick Fit
            sizes = {} # Guarda a quantidade de vezes que cada tamanho eh requisitado
            for process in processes:
                size = math.ceil(process.b/self.s)*self.s
                if (str(size) in sizes):
                    sizes[str(size)] += 1
                else:
                    sizes[str(size)] = 1
            # Tamanhos mais requisitados (25% da quantidade de tamanhos)
            top_sizes = sorted(sizes, key=sizes.get, reverse=True)[:int(len(sizes)/4)]
            for size in top_sizes:
                self.quick_list[str(size)] = []
                for i in range(0, self.virtual-int(size)+1, self.s):
                    self.quick_list[str(size)].append(i)
            self.quick_node["0"] = (None, self.root) # (pre_node, node)

    ############################################################################
    # Atualiza o bit R
    def update_R_bit (self):
        if (self.id_sub == 4): #  Least Recently Used (Quarta versao)
            page = self.root_page
            while (page != None):
                page.counter = page.counter >> 1
                page = page.next_page

    ############################################################################
    # Compacta a memoria
    def compact (self):
        # Memoria Virtual
        if (self.debug):
            print(Color.BLUE + "* Memoria compactada" + Color.END)
        free_space = 0
        pre_node = None
        node = self.root
        while (node != None):
            if (node.pid == -1):
                free_space += node.size
                if (pre_node != None):
                    pre_node.next_node = node.next_node
                else:
                    self.root = node.next_node
            else:
                node.base -= free_space
                pre_node = node
            node = node.next_node
        free_node = None
        if (pre_node != None):
            pre_node.next_node = free_node = Node(-1, pre_node.base + pre_node.size, free_space, None)
        else:
            self.root = free_node = Node(-1, 0, free_space, None)
        if (self.id_fit == 3): # Quick Fit
            # Atualiza as listas
            for s in self.quick_list:
                spaces_s = self.quick_list[s] = [] # Reseta a lista do espaco s
                for i in range(free_node.base, self.virtual-int(s)+1, self.s):
                    self.quick_list[str(s)].append(i)
            # Atualiza o acesso rapido
            self.quick_node = {} # Reseta a lista de acessos rapidos
            self.quick_node[str(free_node.base)] = (pre_node, free_node) # (pre_node, node)
        ########################################################################
        # Memoria Fisica
        free_page = None
        pre_page = None
        page = self.root_page
        while (page != None):
            if (page.pid == -1):
                tmp_next_page = page.next_page
                if (pre_page != None):
                    pre_page.next_page = page.next_page
                else:
                    self.root_page = page.next_page
                page.next_page = free_page
                free_page = page
                page = tmp_next_page
            else:
                pre_page = page
                page = page.next_page
        if (pre_page != None):
            pre_page.next_page = free_page
        else:
            self.root_page = free_page
        # Atualiza os arquivos das memorias
        self.update_memory_files()

    ############################################################################
    # Aloca um espaco de tamanho b na memoria virtual para o processo pid
    def allocate (self, process):
        ########################################################################
        # Procura um espaco livre na memoria virtual
        start_time = time.time()
        if (self.id_fit == 1): # Best Fit
            pre_node, node = self.best_fit(process.b)
        elif (self.id_fit == 2): # Worst Fit
            pre_node, node = self.worst_fit(process.b)
        elif (self.id_fit == 3): # Quick Fit
            pre_node, node = self.quick_fit(process.b)
        # Tempo necessario para encontrar um espaco livre na memoria
        end_time = time.time()
        self.allocate_time += end_time - start_time
        ########################################################################
        if (node.base + process.b != self.virtual):
            new_node = Node(process.pid, node.base, process.b, node)
        else:
            new_node = Node(process.pid, node.base, process.b, None)
        if (pre_node == None):
            self.root = new_node
        else:
            pre_node.next_node = new_node
        node.base += process.b
        node.size -= process.b
        if (node.next_node != None and node.base == node.next_node.base):
            node = node.next_node
            new_node.next_node = node
        if (self.id_fit == 3): # Quick Fit
            # Atualiza as listas
            for s in self.quick_list:
                spaces_s = self.quick_list[s] # Lista do espaco s
                to_remove = []
                for position in spaces_s:
                    if (new_node.base + new_node.size <= position):
                        break
                    if (new_node.base < position + int(s)):
                        to_remove.append(position)
                for position in to_remove:
                    spaces_s.remove(position)
            # Atualiza o acesso rapido
            del self.quick_node[str(new_node.base)] # Remove o acesso ao node que acabou de ser ocupado
            # Adiciona um novo acesso rapido ao Node livre seguinte
            if (node.base != self.virtual and new_node.next_node != None and new_node.next_node.pid == -1):
                self.quick_node[str(node.base)] = (new_node, node)
        # Atualiza o arquivo da Memoria Virtual
        self.write(self.vir_file, process.pid, new_node.base, process.b)

    ############################################################################
    # Desaloca o processo pid da memoria virtual
    def deallocate (self, process):
        pre2_node = None
        pre_node = None
        node = self.root
        while (node != None):
            if (node.pid == process.pid):
                node.pid = -1
                pre_free_node = pre_node
                free_node = node
                # Fusao com o Node seguinte
                if (node.next_node != None and node.next_node.pid == -1):
                    node.size += node.next_node.size
                    node.next_node = node.next_node.next_node
                # Fusao com o Node anterior
                if (pre_node != None and pre_node.pid == -1):
                    pre_free_node = pre2_node
                    free_node = pre_node
                    pre_node.size += node.size
                    pre_node.next_node = node.next_node
                if (self.id_fit == 3): # Quick Fit
                    # Atualiza as listas
                    for s in self.quick_list:
                        for i in range(free_node.base, node.base+node.size-int(s)+1, self.s):
                            if (i not in self.quick_list[str(s)]):
                                self.quick_list[str(s)].append(i)
                        self.quick_list[str(s)].sort()
                    # Atualiza o acesso rapido
                    for i in range(free_node.base+self.s, free_node.base+free_node.size, self.s):
                        if (str(i) in self.quick_node):
                            del self.quick_node[str(i)]
                    self.quick_node[str(free_node.base)] = (pre_free_node, free_node)
                # Atualiza o arquivo da Memoria Virtual
                self.write(self.vir_file, -1, node.base, process.b)
                break
            pre2_node = pre_node
            pre_node = node
            node = node.next_node

    ############################################################################
    # Remove as paginas do processo pid que estao na memoria fisica
    def remove_pages_from_process (self, process):
        page = self.root_page
        base = 0
        while (page != None):
            if (page.pid == process.pid):
                page.pid = -1
                page.b = 0
                page.part = 0
                if (self.id_sub == 1): # Optimal
                    page.label = -1
                elif (self.id_sub == 2): # First-In, First-Out
                    self.pages_queue.remove(page)
                elif (self.id_sub == 3): # Least Recently Used (Segunda versao)
                    for i in range(self.n_pages):
                        self.pages_matrix[page.page_id][i] = 0
                elif (self.id_sub == 4): #  Least Recently Used (Quarta versao)
                    page.counter = 0
                # Atualiza o arquivo da Memoria Fisica
                self.write(self.mem_file, -1, base, self.p)
            base += self.p
            page = page.next_page

    ############################################################################
    # Acessa a memoria fisica
    def access (self, process, part):
        # Verifica se a pagina ja esta carregada
        # Aproveita e guarda a primeira pagina livre (que talvez pode ser usada)
        free_page = None
        page = self.root_page
        while (page != None):
            if (free_page == None and page.pid == -1):
                free_page = page
            if (page.pid == process.pid and page.part == part): # Ja esta carregada
                if (self.id_sub == 1): # Optimal
                    # Verifica se o processo vai acessar essa pagina novamente no futuro
                    page.label = -1
                    for access in process.accesses:
                        access_time, access_position = access
                        access_part = int(access_position/self.p)
                        if (access_part == part):
                            page.label = access_time # Marco o tempo que a pagina sera acessada
                            break
                elif (self.id_sub == 2): # First-In, First-Out
                    self.pages_queue.remove(page)
                    self.pages_queue.append(page)
                elif (self.id_sub == 3): # Least Recently Used (Segunda versao)
                    for i in range(self.n_pages):
                        self.pages_matrix[page.page_id][i] = 1
                        self.pages_matrix[i][page.page_id] = 0
                elif (self.id_sub == 4): #  Least Recently Used (Quarta versao)
                    page.counter = page.counter | 2**7
                return
            page = page.next_page
        # Verifica se ha uma pagina livre
        page = free_page
        if (page == None): # Page Fault
            self.page_faults += 1
            if (self.debug):
                print(Color.YELLOW + "  * Page Fault" + Color.END)
            if (self.id_sub == 1): # Optimal
                page = self.optimal()
            elif (self.id_sub == 2): # First-In, First-Out
                page = self.fifo()
            elif (self.id_sub == 3): # Least Recently Used (Segunda versao)
                page = self.lru_2()
            elif (self.id_sub == 4): #  Least Recently Used (Quarta versao)
                page = self.lru_4()
        if (self.id_sub == 1): # Optimal
            # Verifica se o processo vai acessar essa pagina novamente no futuro
            page.label = -1
            for access in process.accesses:
                access_time, access_position = access
                access_part = int(access_position/self.p)
                if (access_part == part):
                    page.label = access_time # Marco o tempo que a pagina sera acessada
                    break
        elif (self.id_sub == 2): # First-In, First-Out
            self.pages_queue.append(page)
        elif (self.id_sub == 3): # Least Recently Used (Segunda versao)
            for i in range(self.n_pages):
                self.pages_matrix[page.page_id][i] = 1
                self.pages_matrix[i][page.page_id] = 0
        elif (self.id_sub == 4): #  Least Recently Used (Quarta versao)
            page.counter = 2**7
        # Altera o conteudo da pagina
        page.pid = process.pid
        page.b = process.b
        page.part = part
        # Atualiza o arquivo da Memoria Fisica
        p = self.root_page
        base = 0
        while (p != None):
            if (p.page_id == page.page_id):
                break
            base += self.p
            p = p.next_page
        b = min(self.p, page.b)
        self.write(self.mem_file, page.pid, base, b) # Parte do processo
        self.write(self.mem_file, -1, base+b, self.p-b) # Resto da pagina

################################################################################
    # Algoritmo Best Fit (Gerencia de espaco livre)
    def best_fit (self, b):
        pre_min_node = pre_node = None
        min_node = node = self.root
        min_size = self.virtual
        while (node != None):
            if (node.pid == -1 and node.size >= b and node.size < min_size):
                pre_min_node = pre_node
                min_node = node
                min_size = node.size
            pre_node = node
            node = node.next_node
        return pre_min_node, min_node

    ############################################################################
    # Algoritmo Worst Fit (Gerencia de espaco livre)
    def worst_fit (self, b):
        pre_max_node = pre_node = None
        max_node = node = self.root
        max_size = 0
        while (node != None):
            if (node.pid == -1 and node.size >= b and node.size > max_size):
                pre_max_node = pre_node
                max_node = node
                max_size = node.size
            pre_node = node
            node = node.next_node
        return pre_max_node, max_node

    ############################################################################
    # Algoritmo Quick Fit (Gerencia de espaco livre)
    def quick_fit (self, b):
        try:
            # Lista dos enderecos dos espacos que comportam o tamanho b
            spaces_b = self.quick_list[str(b)]
            position = min(spaces_b) # Menor endereco da lista
            return self.quick_node[str(position)]
        except KeyError: # Se o tamanho b nao estiver na lista do quick
            return self.best_fit(b) # Usa o algoritmo Best Fit

################################################################################
    # Algoritmo Optimal (Substituicao de pagina)
    def optimal (self):
        optimal_page = page = self.root_page
        while (page != None):
            if (page.label == -1): # A pagina nao vai mais ser acessada
                optimal_page = page
                break
            if (page.label > optimal_page.label):
                optimal_page = page
            page = page.next_page
        return optimal_page

    ############################################################################
    # Algoritmo First-In, First-Out (Substituicao de pagina)
    def fifo (self):
        page = self.pages_queue[0]
        del self.pages_queue[0]
        return page

    ############################################################################
    # Algoritmo Least Recently Used - Segunda versao (Substituicao de pagina)
    def lru_2 (self):
        id_min = 0
        min_value = 2**self.n_pages
        for i in range(self.n_pages):
            line_value = int("".join(str(x) for x in self.pages_matrix[i]), 2)
            if (line_value < min_value):
                min_value = line_value
                id_min = i
        page = self.root_page
        while (page != None):
            if (page.page_id == id_min):
                break
            page = page.next_page
        return page

    ############################################################################
    # Algoritmo Least Recently Used - Quarta versao (Substituicao de pagina)
    def lru_4 (self):
        lru_page = page = self.root_page
        while (page != None):
            if (page.counter < lru_page.counter):
                lru_page = page
            page = page.next_page
        return lru_page

################################################################################
# No da lista ligada
class Node (object):
    ############################################################################
    # Construtor
    def __init__ (self, pid, base, size, next_node):
        self.pid = pid # PID do processo que esta ocupando este Node (-1 se estiver livre)
        self.base = base # Primeiro endereco do Node
        self.size = size # Quantidade de enderecos do Node
        self.next_node = next_node # Proximo Node

################################################################################
# Pagina (No da lista ligada)
class Page (object):
    ############################################################################
    # Construtor
    def __init__ (self, page_id, pid, b, part, next_page):
        self.page_id = page_id # Identificador da pagina
        self.pid = pid # PID do processo que esta ocupando esta pagina (-1 se estiver livre)
        self.b = b # Tamanho da parte do processo que esta na pagina (na pratica eh <= p)
        self.part = part # Parte do processo que esta na pagina
        self.next_page = next_page # Proxima pagina
        # Estruturas especiais para os algoritmos de substituicao
        self.counter = 0 # Contador (LRU 4)
        self.label = -1 # Rotulo (Optimal) - Indica o tempo que a pagina sera acessada novamente

################################################################################
