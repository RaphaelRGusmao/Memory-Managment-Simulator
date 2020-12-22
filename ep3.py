################################################################################
#                                IME-USP (2017)                                #
#                    MAC0422 - Sistemas Operacionais - EP3                     #
#                                                                              #
#                                    Shell                                     #
#                                                                              #
#                              Raphael R. Gusmao                               #
################################################################################

import readline
import simulator

# Cores
class Color:
    CYAN   = '\033[36;1m' # Azul claro
    BLUE   = '\033[34;1m' # Azul
    GREEN  = '\033[32;1m' # Verde
    PINK   = '\033[35;1m' # Rosa
    YELLOW = '\033[33;1m' # Amarelo
    END    = '\033[0m'    # Para de pintar

# Algoritmos
fit = {
    1: "Best Fit",
    2: "Worst Fit",
    3: "Quick Fit"
}
sub = {
    1: "Optimal",
    2: "First-In, First-Out",
    3: "Least Recently Used (Segunda Versao)",
    4: "Least Recently Used (Quarta Versao)"
}

# Parametros
trace_file_loaded = False
id_fit = 0
id_sub = 0
debug = False

################################################################################
# (Miii) Shell (ma belle...)
def shell ():
    global trace_file_loaded, id_fit, id_sub, debug
    print(Color.CYAN + "+------------------------------------------------------------------+" + Color.END)
    print(Color.CYAN + "|                          IME-USP (2017)                          |" + Color.END)
    print(Color.CYAN + "|              MAC0422 - Sistemas Operacionais - EP3               |" + Color.END)
    print(Color.CYAN + "|                        Raphael R. Gusmao                         |" + Color.END)
    print(Color.CYAN + "+------------------------------------------------------------------+" + Color.END)
    while (True):
        command = input(Color.CYAN + "[ep3]: " + Color.END)
        if command.upper() == "SAI":
            break
        command = command.split()
        if (len(command) == 0):
            continue
        ########################################################################
        elif (command[0].upper() == "CARREGA"):
            if (len(command) != 2):
                print(Color.YELLOW + "\tUso: carrega <arquivo>" + Color.END)
            else :
                try:
                    trace_file_loaded = simulator.load_file(command[1])
                    print(Color.GREEN + "\tArquivo \"" + command[1] + "\" carregado" + Color.END)
                except FileNotFoundError:
                    print(Color.YELLOW + "\tArquivo \"" + command[1] + "\" nao encontrado" + Color.END)
        ########################################################################
        elif (command[0].upper() == "ESPACO"):
            if (len(command) != 2):
                print(Color.YELLOW + "\tUso: espaco <num>" + Color.END)
            else :
                if (command[1].isdigit() and 1 <= int(command[1]) and int(command[1]) <= 3):
                    id_fit = int(command[1])
                    print(Color.GREEN + "\tAlgoritmo \"" + fit[id_fit] + "\" selecionado" + Color.END)
                else :
                    print(Color.YELLOW + "\tParametro invalido" + Color.END)
        ########################################################################
        elif (command[0].upper() == "SUBSTITUI"):
            if (len(command) != 2):
                print(Color.YELLOW + "\tUso: substitui <num>" + Color.END)
            else :
                if (command[1].isdigit() and 1 <= int(command[1]) and int(command[1]) <= 4):
                    id_sub = int(command[1])
                    print(Color.GREEN + "\tAlgoritmo \"" + sub[id_sub] + "\" selecionado" + Color.END)
                else :
                    print(Color.YELLOW + "\tParametro invalido" + Color.END)
        ########################################################################
        elif (command[0].upper() == "EXECUTA"):
            if (trace_file_loaded == False):
                print(Color.YELLOW + "\tNenhum arquivo carregado" + Color.END)
            if (id_fit == 0):
                print(Color.YELLOW + "\tNenhum algoritmo de gerenciamento de espaco livre escolhido" + Color.END)
            if (id_sub == 0):
                print(Color.YELLOW + "\tNenhum algoritmo de substituicao de pagina escolhido" + Color.END)
            if (trace_file_loaded == False or id_fit == 0 or id_sub == 0):
                continue
            if (len(command) != 2):
                print(Color.YELLOW + "\tUso: executa <intervalo>" + Color.END)
            else :
                if (command[1].isdigit() and int(command[1]) >= 0):
                    simulator.simulate(id_fit, id_sub, int(command[1]), debug)
                else :
                    print(Color.YELLOW + "\tParametro invalido" + Color.END)
        ########################################################################
        elif (command[0].upper() == "DEBUG"):
            if (debug):
                debug = False
                print(Color.GREEN + "\tModo Debug desativado" + Color.END)
            else:
                debug = True
                print(Color.GREEN + "\tModo Debug ativado" + Color.END)
        ########################################################################
        else:
            print(Color.YELLOW + "\tComando invalido!" + Color.END)
    print(Color.CYAN + "+------------------------------------------------------------------+" + Color.END)

################################################################################
# Funcao principal
def main ():
    shell()
if __name__ == "__main__":
    main()

################################################################################
