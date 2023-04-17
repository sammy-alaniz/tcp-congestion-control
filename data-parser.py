import re
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

OUTPUT_DIR_PLOTS = './plots-fairness'
#DATA_DIR = './duration-one-2000-duration-two-1750-sleep-250'
DATA_DIR = './duration-one-1000-duration-two-1000-sleep-0'
ALGO_DIRS = ['reno', 'cubic', 'vegas', 'westwood']
DELAY_DIRS = ['21_miliseconds', '81_miliseconds', '162_miliseconds']

def parse_iperf_data(file_path : str, start_point : int) -> pd.DataFrame:
    file_data = None

    with open(file_path, 'r') as file:
        file_data = file.read()

    # Extract relevant lines
    lines = file_data.strip().split("\n")
    filtered_lines = []
    for line in lines:
        if re.match(r'\[\s*\d+\]', line):
            filtered_lines.append(line)

    lines = filtered_lines

    # Extract columns from lines
    parsed_data = []
    b = start_point
    for i, line in enumerate(lines):
        match = re.match(r'\[\s*(\d+)\]\s*([\d.]+)-([\d.]+)\s*sec\s*([\d.]+)\s*MBytes\s*([\d.]+)\s*Mbits/sec', line)
        if match:
            id, interval_start, interval_end, transfer, bandwidth = match.groups()
            parsed_data.append([b, float(transfer), float(bandwidth)])
            b = b + 1

    # Create a DataFrame and set column names
    df = pd.DataFrame(parsed_data, columns=['ID','Transfer_MBytes', 'Bandwidth_Mbits/sec'])
    
    #print(df)
    return df
    

def parse_ss_data(file_path : str, start_point : int) -> pd.DataFrame:

    file_data = None
    regex_data = None

    cwnd_regex = re.compile(r'\bcwnd:(\d+)\b')

    with open(file_path,'r') as file:
        file_data = file.read()

    regex_data = cwnd_regex.findall(file_data)
    
    parsed_data = []
    b = start_point
    for i, data_point in enumerate(regex_data):
        parsed_data.append([b, float(data_point)])
        b = b + 1

    df = pd.DataFrame(parsed_data, columns=['ID','Cwnd'])
    #print(df)
    return df



def merge_df(df_one : pd.DataFrame, df_two : pd.DataFrame) -> pd.DataFrame:
    all_data_df = pd.merge(df_one, df_two, on='ID', how='left')
    #print(all_data_df)
    return all_data_df




if __name__ == '__main__':
    for algo_dir in ALGO_DIRS:
        for delay_dir in DELAY_DIRS:
            correct = subprocess.run(['mkdir', '-p', f'{OUTPUT_DIR_PLOTS}/{algo_dir}/{delay_dir}'])

            h1_h3_ss_df = parse_ss_data(f'{DATA_DIR}/{algo_dir}/{delay_dir}/host-one-ss-out.txt', 0)
            h1_h3_iperf_df = parse_iperf_data(f'{DATA_DIR}/{algo_dir}/{delay_dir}/iperf_test_h1-h3_15s.txt', 0)

            h2_h4_ss_df = parse_ss_data(f'{DATA_DIR}/{algo_dir}/{delay_dir}/host-two-ss-out.txt', 0)
            h2_h4_iperf_df = parse_iperf_data(f'{DATA_DIR}/{algo_dir}/{delay_dir}/iperf_test_h2-h4_15s.txt', 0)

            h1_h3_ss_iperf_df = merge_df(h1_h3_ss_df, h1_h3_iperf_df)
            h2_h4_ss_iperf_df = merge_df(h2_h4_ss_df, h2_h4_iperf_df)

            # Since tcp flow 2 starts 250s after flow 1, offset the x axis values
            offset = len(h1_h3_ss_iperf_df) - len(h2_h4_ss_iperf_df)
            h2_h4_ss_iperf_df['ID'] = h2_h4_ss_iperf_df['ID'] + offset

            h1_h3_ss_iperf_df = h1_h3_ss_iperf_df.iloc[::15, :]
            h2_h4_ss_iperf_df = h2_h4_ss_iperf_df.iloc[::15, :]

            line_width = 1

            plt.figure(figsize=(8,6))
            plt.plot(h1_h3_ss_iperf_df['ID'], h1_h3_ss_iperf_df['Cwnd'], label='TCP Flow 1', linestyle='-', linewidth=line_width)
            plt.plot(h2_h4_ss_iperf_df['ID'], h2_h4_ss_iperf_df['Cwnd'], label='TCP Flow 2', linestyle='-', linewidth=line_width)
            plt.xlabel('Time (seconds)')
            plt.ylabel('Cwnd (packets)')
            plt.legend()
            plt.savefig(f'{OUTPUT_DIR_PLOTS}/{algo_dir}/{delay_dir}/cwnd_v_time.png')
            plt.close()

            # h1_h3_ss_iperf_df = h1_h3_ss_iperf_df.iloc[::20, :]
            # h2_h4_ss_iperf_df = h2_h4_ss_iperf_df.iloc[::20, :]

            plt.figure(figsize=(8,6))
            plt.plot(h1_h3_ss_iperf_df['ID'], h1_h3_ss_iperf_df['Bandwidth_Mbits/sec'], label='TCP Flow 1', linestyle='-', linewidth=line_width)
            plt.plot(h2_h4_ss_iperf_df['ID'], h2_h4_ss_iperf_df['Bandwidth_Mbits/sec'], label='TCP Flow 2', linestyle='-', linewidth=line_width)
            plt.xlabel('Time (seconds)')
            plt.ylabel('Throughput (Mbps)')
            plt.legend()
            plt.savefig(f'{OUTPUT_DIR_PLOTS}/{algo_dir}/{delay_dir}/throughput_v_time.png')
            plt.close()


