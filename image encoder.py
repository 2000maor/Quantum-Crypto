# authors: Maor Marcus & Roy Mazuz
from datetime import datetime
from qiskit import (execute, Aer)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from PIL import Image


N = 8  # the number of the qubits we need in order to create 256 different quantum states
INPUTNAME, ENCRYPTNAME, DECRYPTNAME = "input.jpg", "encryption.jpg", "decryption.jpg"  # the filenames we use in the
SIMULATOR = Aer.get_backend('qasm_simulator')  # creating quantum simulator using qiskit library


def create_bell_state_circuit():
    alice_qubits = QuantumRegister(N, 'a')  # Alice (sender) has a register of 8 bits
    alice_cbits = ClassicalRegister(N,
                                    'ac')  # Alice has a register of 8 classical bits (for measurement of the qubits)
    bob_qubits = QuantumRegister(N, 'b')  # Bob (receiver) has a register of 8 qubits
    bob_cbits = ClassicalRegister(N, 'bc')  # Bob also has a register of 8 classical bits

    circuit = QuantumCircuit(alice_qubits, bob_qubits, alice_cbits, bob_cbits)  # creating the circuit of Alice & Bob
    circuit.h(range(N))  # applying Hadamard gate on each qubit in order to create random number in range [0, 2^8 - 1]
    for m in range(N):
        circuit.cx(m,
                   m + N)  # applying Controlled NOT (CX) gates, Alice's reg is the control and Bob's reg is the target
    circuit.measure(range(2 * N), range(2 * N))  # getting the result by measuring the qubits
    circuit.draw(output='mpl', filename='randomizer.png')  # saving an image of the circuit
    return circuit


def create_not_entangled_circuit():
    alice_qubits = QuantumRegister(N, 'a')  # Alice (sender) has a register of 8 bits
    alice_cbits = ClassicalRegister(N,
                                    'ac')  # Alice has a register of 8 classical bits (for measurement of the qubits)
    bob_qubits = QuantumRegister(N, 'b')  # Bob (receiver) has a register of 8 qubits
    bob_cbits = ClassicalRegister(N, 'bc')  # Bob also has a register of 8 classical bits

    circuit = QuantumCircuit(alice_qubits, bob_qubits, alice_cbits, bob_cbits)  # creating the circuit of Alice & Bob
    circuit.h(range(2 * N))  # applying Hadamard gate on each qubit to create random number in range [0, 2^8 - 1]
    circuit.measure(range(2 * N), range(2 * N))  # getting the result by measuring the qubits
    circuit.draw(output='mpl', filename='randomizer.png')  # saving an image of the circuit
    return circuit


def create_half_entangled_circuit():
    alice_qubits = QuantumRegister(N, 'a')  # Alice (sender) has a register of 8 bits
    alice_cbits = ClassicalRegister(N,
                                    'ac')  # Alice has a register of 8 classical bits (for measurement of the qubits)
    bob_qubits = QuantumRegister(N, 'b')  # Bob (receiver) has a register of 8 qubits
    bob_cbits = ClassicalRegister(N, 'bc')  # Bob also has a register of 8 classical bits

    circuit = QuantumCircuit(alice_qubits, bob_qubits, alice_cbits, bob_cbits)  # creating the circuit of Alice & Bob
    circuit.h(range(N))  # applying Hadamard gate on each qubit to create random number in range [0, 2^8 - 1]
    for m in range(N):
        circuit.ch(m,
                   m + N)  # applying Controlled Hadamard (CH) gates, Alice's reg is control and Bob's reg is the target
    circuit.measure(range(2 * N), range(2 * N))  # getting the result by measuring the qubits
    circuit.draw(output='mpl', filename='randomizer.png')  # saving an image of the circuit
    return circuit


def true_random(circuit):
    """ Creating a quantum randomizer of a number between 0 and 255 (allowed pixel color values) using a quantum circuit
        The function entangles alice's qubits with bob's, using Hadamard & C-NOT gates (alice is the control, bob is
        the target). The function returns alice's abd bob's classical registers after they measure their qubits """
    job = execute(circuit, SIMULATOR, shots=1)  # executing the circuit we created before
    result = job.result()
    counts = result.get_counts(circuit)
    state = max(counts, key=counts.get)
    return int(state[:N], 2), int(state[N + 1:], 2)


def bitwise_xor(tup1, tup2):
    """ Gets two tuples with the same length, returns a tuple that stores the bitwise xor between the input tuples """
    xor_arr = []
    for k in range(len(tup1)):
        xor_arr.append(tup1[k] ^ tup2[k])
    return tuple(xor_arr)


def encrypt_image(input_name, output_name, circuit):
    """ Gets names of image files - input & output.
        Returns an output image file (.jpg, .jpeg or .png) contains the input image, encoded, using random bits """
    key = []  # array with all of the measurements that Bob will take (after Alice will measure her qubits)
    im = Image.open(input_name)
    old_pixels = im.load()
    im.show()
    img = Image.new(im.mode, im.size)
    new_pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            meas1, meas2, meas3 = true_random(circuit), true_random(circuit), true_random(circuit)
            new_pixels[i, j] = bitwise_xor(old_pixels[i, j], (meas1[0], meas2[0], meas3[0]))
            key.append((meas1[1], meas2[1], meas3[1]))
    img.save(output_name)
    img.show()
    return img, key


def decrypt_image(input_image, output_name, key):
    """  gets names of image files - input & output, and a key array of tuples pixel values: (0-255,0-255,0-255).
         The function decrypts the input image using the key, and stores the result in the output image
         returns the decrypted image file """
    old_pixels = input_image.load()
    img = Image.new(input_image.mode, input_image.size)
    new_pixels = img.load()
    for i in range(img.size[0]):
        col = i * img.size[1]
        for j in range(0, img.size[1]):
            new_pixels[i, j] = bitwise_xor(old_pixels[i, j], (key[col + j][0], key[col + j][1], key[col + j][2]))
    img.save(output_name)
    img.show()
    return img


# -------------- creation of the quantum circuits that will give us the entangled random numbers --------------

q_circuits = [create_bell_state_circuit(), create_not_entangled_circuit(), create_half_entangled_circuit()]

# --------------------- time tests for creation of random numbers using the quantum circuit above ---------------------

"""
starting_time = datetime.now()
for i in range(3):
    for x in range(100*10**i):
        true_random()
    ending_time = datetime.now()
    print("For", 100*10**i, "entangled random numbers:")
    print("1) starting time is: ", starting_time)
    print("2) ending time is: ", ending_time)
    print("----> total computation time:", ending_time - starting_time, "\n")
"""
# --------------------- Encryption and Decryption for each quantum circuit ---------------------

for q_circuit in q_circuits:
    # --------------------- Encryption ---------------------

    starting_time = datetime.now()
    encoded_img, bob_key = encrypt_image(INPUTNAME, ENCRYPTNAME, q_circuit)
    ending_time = datetime.now()
    print("Encryption starting time is: ", starting_time, "\nEncryption ending time is:", ending_time,
          "\n----> Total encryption time:", ending_time - starting_time, "\n")

    # --------------------- Decryption ---------------------

    starting_time = datetime.now()
    decoded_img = decrypt_image(encoded_img, DECRYPTNAME, bob_key)
    ending_time = datetime.now()
    print("Decryption starting time is: ", starting_time, "\nDecryption ending time is:", ending_time,
          "\n----> Total decryption time:", ending_time - starting_time, "\n")
