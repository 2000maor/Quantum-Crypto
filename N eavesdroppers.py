import xlsxwriter
from qiskit import (execute, Aer)
from qiskit import QuantumCircuit


WAY = 'C:\maor\lab\physics lab\year 3\semester B\Quantum cryptography\\'  # the location of this .py file
N = 100  # number of eavesdroppers
FILENAME = str(N) + ' eavesdroppers.xlsx'  # the file we write our data to
LENGTH = 100  # length of the message
EVES = []
for x in range(N):
    EVES.append(["EVE"+str(x)])
    EVES.append(["Bit"])
PEOPLE = [["Alice"], ["Bit"]] + EVES + [["Bob"], ["Bit"]]
WORKBOOK = xlsxwriter.Workbook(FILENAME)
WORKSHEET = WORKBOOK.add_worksheet()


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


def base_randomizer(aeb_arr):
    """ randomize (in quantum terms) N bases that will be used in the BB84 key exchange protocol """
    for x in range(LENGTH):
        for y in range(len(aeb_arr)):
            if y % 2 == 0 or y == 1:
                bit = true_random()
                if y != 1:
                    if bit == '0':
                        aeb_arr[y].append('+')
                    else:
                        aeb_arr[y].append('x')
                else:
                    aeb_arr[y].append(bit)
    return aeb_arr


all_bases = base_randomizer(PEOPLE)  # getting the bases of all the people, and the initial key bits of Alice


def bases_to_excel(bases_arr):
    """ gets the bases and Alice bits and extracts them to an excel sheet as a chart """
    for x in range(len(bases_arr)):
        base = bases_arr[x]
        for y in range(len(base)):
            WORKSHEET.write(y, x, base[y])  # Writes the base to the excel sheet


bases_to_excel(all_bases)


def experiment_with_n_eavesdroppers(bases_arr):
    """ gets the bases and extracts them to an excel sheet as a chart """
    for x in range(3, len(bases_arr), 2):
        base1_list, base2_list, bit_list = bases_arr[x - 3], bases_arr[x - 1], bases_arr[x - 2]
        for y in range(1, len(base1_list)):
            base1, base2, bit = base1_list[y], base2_list[y], bit_list[y]
            if base1 == base2:
                WORKSHEET.write(y, x, bit)  # Writes the bits
                bases_arr[x].append(bit)  # updates the bit list
            else:
                rand = true_random()
                WORKSHEET.write(y, x, rand)  # Writes the bits
                bases_arr[x].append(rand)  # updates the bit list
    WORKBOOK.close()


experiment_with_n_eavesdroppers(all_bases)
