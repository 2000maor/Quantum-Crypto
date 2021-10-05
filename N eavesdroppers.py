# authors: Maor Marcus & Roy Mazuz
import xlsxwriter
import copy
from qiskit import (execute, Aer)
from qiskit import QuantumCircuit


N, M, LENGTH = 50, 10, 100  # N - number of eavesdroppers, M - number of experiments, L - length of the message
FILENAME = str(N) + ' eavesdroppers.xlsx'  # the file we write our data to
EVES = []
for x in range(N):
    EVES.append(["EVE"+str(x)])
    EVES.append(["Bit"])
PEOPLE = [["Alice"], ["Bit"]] + EVES + [["Bob"], ["Bit"]]
WORKBOOK = xlsxwriter.Workbook(FILENAME)
WORKSHEETS = []
for x in range(M):
    WORKSHEETS.append(WORKBOOK.add_worksheet())


def true_random():
    """ creating a real randomizer in order to choose the basis """
    simulator = Aer.get_backend('qasm_simulator')
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    job = execute(circuit, simulator, shots=1000)
    result = job.result()
    counts = result.get_counts(circuit)
    return str(max(counts, key=counts.get))


def base_randomizer(random_bases):
    """ randomize (in quantum terms) N bases that will be used in the BB84 key exchange protocol """
    for x in range(LENGTH):
        for y in range(len(PEOPLE)):
            if y % 2 == 0 or y == 1:
                bit = true_random()
                if y != 1:
                    if bit == '0':
                        random_bases[y].append('+')
                    else:
                        random_bases[y].append('x')
                else:
                    random_bases[y].append(bit)
    return random_bases


def bases_to_excel(bases_arr, worksheet):
    """ gets the bases and Alice bits and extracts them to an excel sheet as a chart """
    for x in range(len(bases_arr)):
        base = bases_arr[x]
        for y in range(len(base)):
            worksheet.write(y, x, base[y])  # Writes the base to the excel sheet


def experiment_with_n_eavesdroppers(bases_arr, worksheet):
    """ gets the bases and extracts them to an excel sheet as a chart """
    for x in range(3, len(bases_arr), 2):
        base1_list, base2_list, bit_list = bases_arr[x - 3], bases_arr[x - 1], bases_arr[x - 2]
        for y in range(1, len(base1_list)):
            base1, base2, bit = base1_list[y], base2_list[y], bit_list[y]
            if base1 == base2:
                worksheet.write(y, x, bit)  # Writes the bits
                bases_arr[x].append(bit)  # updates the bit list
            else:
                rand = true_random()
                worksheet.write(y, x, rand)  # Writes the bits
                bases_arr[x].append(rand)  # updates the bit list


for x in range(M):
    people_list = copy.deepcopy(PEOPLE)
    all_bases = base_randomizer(people_list)  # getting the bases of all the people, and the initial key bits of Alice
    bases_to_excel(all_bases, WORKSHEETS[x])
    experiment_with_n_eavesdroppers(all_bases, WORKSHEETS[x])
WORKBOOK.close()
