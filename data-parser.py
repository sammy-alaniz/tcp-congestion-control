import re
import pandas as pd
import matplotlib.pyplot as plt


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
    
    print(df)
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
    print(df)
    return df



def merge_df(df_one : pd.DataFrame, df_two : pd.DataFrame) -> pd.DataFrame:
    all_data_df = pd.merge(df_one, df_two, on='ID', how='left')
    print(all_data_df)
    return all_data_df




if __name__ == '__main__':
    h1_h3_ss_df = parse_ss_data('host-one-ss-out.txt',0)
    h1_h3_iperf_df = parse_iperf_data('iperf_test_h1-h3_15s.txt',0)

    h2_h4_ss_df = parse_ss_data('host-two-ss-out.txt',5)
    h2_h4_iperf_df = parse_iperf_data('iperf_test_h2-h4_15s.txt',5)

    h1_h3_ss_iperef_df = merge_df(h1_h3_ss_df, h1_h3_iperf_df)

    h1_h3_ss_iperef_df.plot(x='ID', y='Cwnd', kind='line')
    plt.savefig('test.png')