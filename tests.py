################################################################################
#                                IME-USP (2017)                                #
#                    MAC0422 - Sistemas Operacionais - EP3                     #
#                                                                              #
#                                    Testes                                    #
#                                                                              #
#                              Raphael R. Gusmao                               #
################################################################################

import math
from xlwt import Workbook
import xlsxwriter
import simulator
import ep3

trace_file = "trace" # Arquivo de trace

# Algoritmos
fit = 3
sub = 4

measurements = 30 # Numero de medicoes

################################################################################
def output_to_excel (mean_time_results, interval_time_results, faults_results):
    workbook = xlsxwriter.Workbook("Tests.xlsx")
    time_sheet = workbook.add_worksheet("Elapsed Time")
    faults_sheet = workbook.add_worksheet("Page Faults")
    for i in range(fit):
        time_sheet.write(i+1, 0, ep3.fit[i+1])
        faults_sheet.write(i+1, 0, ep3.fit[i+1])
    for j in range(sub):
        time_sheet.write(0, j+1, ep3.sub[j+1])
        faults_sheet.write(0, j+1, ep3.sub[j+1])
    for i in range(fit):
        for j in range(sub):
            time_sheet.write(i+1, j+1, mean_time_results[i][j])
            time_sheet.write(i+1, j+sub+2, interval_time_results[i][j])
            faults_sheet.write(i+1, j+1, faults_results[i][j])
    workbook.close()

################################################################################
def get_statistics (times):
    mean_time = 0; interval_time = 0
    for i in range(measurements):
        mean_time += times[i]
    mean_time /= measurements
    for i in range(measurements):
        interval_time += (times[i]-mean_time)*(times[i]-mean_time)
    interval_time = 1.96*math.sqrt(interval_time/(measurements-1))/math.sqrt(measurements)
    return mean_time, interval_time

################################################################################
def execute (fit, sub):
    simulator.load_file(trace_file)
    simulator.simulate(fit, sub, 0, False)
    return simulator.mean_time_fit*1000000, simulator.page_faults

################################################################################
def main ():
    mean_time_results = [[0 for j in range(sub)] for i in range(fit)]
    interval_time_results = [[0 for j in range(sub)] for i in range(fit)]
    faults_results = [[0 for j in range(sub)] for i in range(fit)]
    for i in range(fit):
        for j in range(sub):
            times = []
            page_faults = 0
            for k in range(measurements):
                elapsed_time, page_faults = execute(i+1, j+1)
                times.append(elapsed_time)
            mean_time, interval_time = get_statistics(times)
            mean_time_results[i][j] = round(mean_time, 2)
            interval_time_results[i][j] = interval_time
            faults_results[i][j] = page_faults
    output_to_excel(mean_time_results, interval_time_results, faults_results)
if __name__ == "__main__":
    main()

################################################################################
