import xlsxwriter
import numpy as np
from qiskit import (execute, Aer)
from qiskit import QuantumCircuit


WAY = 'C:\maor\lab\physics lab\year 3\semester B\Quantum cryptography\\'  # the location of this .py file
FILENAME = 'rotator.xlsx'  # the file we write our data to
N, RES = 100, 100  # the number of the mean calculations we want and the resolution we want for the rotator's angle
M = 10  # the number of the measurements we want to do in each mean calculation


def angle_error(p):
    """ gets the probability of getting 0, returns the biased random 0 or 1 """
    simulator = Aer.get_backend('qasm_simulator')
    qc = QuantumCircuit(1, 1)
    initial_state = [np.sqrt(p), np.sqrt(1 - p)]
    qc.initialize(initial_state, 0)
    qc.measure_all()
    # qc.draw(output='mpl', filename='polarization rotator angle.png')  # saving an image of the circuit
    job = execute(qc, simulator, shots=1)
    result = job.result()
    counts = result.get_counts(qc)
    return int(max(counts, key=counts.get)[0])


def mean_angle_error(p, n):
    """ calculates the mean of activating angle_error n times """
    sum = 0
    for k in range(n):
        sum += angle_error(p)
    return sum / n


workbook = xlsxwriter.Workbook(FILENAME)
worksheet = workbook.add_worksheet()
for x in range(RES + 1):
    print(x)
    worksheet.write(0, x, 0.5 * x / RES)
    worksheet.write(0, x + RES, 0.5 + x / RES)
    for y in range(N):
        worksheet.write(y + 1, x, mean_angle_error(0.5 * x / RES, M))  # increase error of angle in each iteration
        worksheet.write(y + 1, x + RES, mean_angle_error(0.5 + 0.5 * x / RES, M))  # now the other way around
workbook.close()
