from dumbbell import *
import os

DELAYS = [21, 81, 162]

ALGOS = ['reno', 'cubic', 'vegas', 'westwood']

starting_working_dir = os.getcwd()

try:

    for algo in ALGOS:

        # make algo folder to hold algo specific data
        if not os.path.exists(algo):
            os.mkdir(algo)

        # change directory to the algo directory
        os.chdir( starting_working_dir + '/' + algo )

        for delay in DELAYS:
            delay_dir = str(delay) + '_miliseconds'

            # make delay folder to hold specific algo/delay data
            if not os.path.exists(delay_dir):
                os.mkdir(delay_dir)
            
            os.chdir( starting_working_dir + '/' + algo + '/' + delay_dir )

            clean_result = subprocess.run(['sudo','mn','-c'], stdout=subprocess.PIPE)
            dumbbell_test(delay, algo)

except SystemExit:
    print('\nprogram ended early')