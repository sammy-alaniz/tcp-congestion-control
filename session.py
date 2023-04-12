from dumbbell import *
import os

DELAYS = [21, 81, 162]

ALGOS = ['reno', 'cubic', 'vegas', 'westwood']

starting_working_dir = os.getcwd()

duration_one = 2000
duration_two = 1750
sleep = 250

test_dir = 'duration-one-' + str(duration_one) + '-duration-two-' + str(duration_two) + '-sleep-' + str(sleep)

starting_working_dir = starting_working_dir + '/' + test_dir

if not os.path.exists(starting_working_dir):
    os.mkdir(starting_working_dir)

try:

    for algo in ALGOS:
        
        # start at original dir
        os.chdir( starting_working_dir )

        # make algo folder to hold algo specific data
        if not os.path.exists(algo):
            os.mkdir(algo)

        for delay in DELAYS:

            # change directory to the algo directory
            os.chdir( starting_working_dir + '/' + algo )

            delay_dir = str(delay) + '_miliseconds'

            # make delay folder to hold specific algo/delay data
            if not os.path.exists(delay_dir):
                os.mkdir(delay_dir)
            
            os.chdir( starting_working_dir + '/' + algo + '/' + delay_dir )

            clean_result = subprocess.run(['sudo','mn','-c'], stdout=subprocess.PIPE)
            dumbbell_test(delay, algo, duration_one, duration_two, sleep)

except SystemExit:
    print('\nprogram ended early')