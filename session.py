from dumbbell import *

DELAYS = [21, 81, 162]

ALGOS = ['reno', 'cubic', 'vegas', 'westwood']

for algo in ALGOS:
    for delay in DELAYS:
        clean_result = subprocess.run(['sudo','mn','-c'], stdout=subprocess.PIPE)
        dumbbell_test(delay, algo)