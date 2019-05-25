# -*- coding: utf-8 -*-

# Copyright 2019 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
import logging
import numpy as np
import random
from qiskit import *
import time


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def get_L(n):
    # determine the size of the grid corresponding to n qubits
    Lx = int(2 ** np.ceil(n / 2))
    Ly = int(2 ** np.floor(n / 2))
    return [Lx, Ly]


def make_grid(n):
    # make a dictionary for which every point in the grid is assigned a unique n bit string
    # these are such that '0'*n is in the center, and each string neighbours only its neighbours on the hypercube

    [Lx, Ly] = get_L(n)

    strings = {}
    for y in range(Ly):
        for x in range(Lx):
            strings[(x, y)] = ''

    for (x, y) in strings:
        for j in range(n):
            if (j % 2) == 0:
                xx = np.floor(x / 2 ** (j / 2))
                strings[(x, y)] = str(int((xx + np.floor(xx / 2)) % 2)) + strings[(x, y)]
            else:
                yy = np.floor(y / 2 ** ((j - 1) / 2))
                strings[(x, y)] = str(int((yy + np.floor(yy / 2)) % 2)) + strings[(x, y)]

    center = '0' * n
    current_center = strings[(int(np.floor(Lx / 2)), int(np.floor(Ly / 2)))]
    diff = ''
    for j in range(n):
        diff += '0' * (current_center[j] == center[j]) + '1' * (current_center[j] != center[j])
    for (x, y) in strings:
        newstring = ''
        for j in range(n):
            newstring += strings[(x, y)][j] * (diff[j] == '0') + (
                        '0' * (strings[(x, y)][j] == '1') + '1' * (strings[(x, y)][j] == '0')) * (diff[j] == '1')
        strings[(x, y)] = newstring

    grid = {}
    for y in range(Ly):
        for x in range(Lx):
            grid[strings[(x, y)]] = (x, y)

    return strings

def normalize_height(Z):
    # scales heights so that the maximum is 1 and the minimum is 0
    maxZ = max(Z.values())
    minZ = min(Z.values())
    for pos in Z:
        Z[pos] = (Z[pos]-minZ)/(maxZ-minZ)
    return Z

def counts2height(counts,grid,log=False):
    # set the height of a point to be the counts value of the corresponding bit string (or the logarithm) and normalize
    Z = {}
    for pos in grid:
        try:
            Z[pos] = counts[grid[pos]]
        except:
            Z[pos] = 0
    if log:
        for pos in Z:
            Z[pos] = max(Z[pos],1/len(grid)**2)
            Z[pos] = np.log( Z[pos] )/np.log(2)
    Z = normalize_height(Z)
    return Z

def height2state(Z, grid):
    # converts a heightmap intp a quantum state
    N = len(grid)
    state = [0]*N

    for pos in Z:
        state[int(grid[pos], 2)] = np.sqrt(Z[pos]) # amplitude is square root of height value
    R = sum(np.absolute(state)**2)
    state = [amp / np.sqrt(R) for amp in state] # amplitudes are normalized
    return state


def state2counts (state,shots=None):
    N = len(state)
    n = int(np.log2(N))
    if shots is None:
        shots = N**2
    counts = {}
    for j in range(N):
        string = bin(j)[2:]
        string = '0'*(n-len(string)) + string
        counts[string] = np.absolute(state[j])**2 * shots # square amplitudes to get probabilities
    return counts


def quantum_tartan(seed, theta, grid=None, shots=1, log=True):
    n = int(np.log2(len(seed)))

    if grid is None:
        grid = make_grid(n)

    state = height2state(seed, grid)

    q = QuantumRegister(n)
    qc = QuantumCircuit(q)
    qc.initialize(state, q)
    qc.ry(2 * np.pi * theta, q)

    if shots > 1:
        try:
            # IBMQ.load_accounts()
            backend = Aer.get_backend('qasm_simulator')  # backend = IBMQ.get_backend('ibmq_16_melbourne')
        except:
            print(
                'An IBMQ account is required to use a real device\nSee https://github.com/Qiskit/qiskit-terra/blob/master/README.md')
    else:
        backend = Aer.get_backend('statevector_simulator')

    if shots > 1:
        c = ClassicalRegister(n)
        qc.add_register(c)
        qc.measure(q, c)

    start = time.time()
    print('Quantum job initiated on', backend.name())
    job = execute(qc, backend, shots=shots)
    end = time.time()
    print('Quantum job complete after', int(end - start), 'seconds')

    if shots > 1:
        counts = job.result().get_counts()
    else:
        counts = state2counts(job.result().get_statevector())

    Z = counts2height(counts, grid, log=log)


    return Z, grid