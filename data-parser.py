import re
import pandas as pd


def parse_iperf_data(file_path : str):
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
    for i, line in enumerate(lines):
        match = re.match(r'\[\s*(\d+)\]\s*([\d.]+)-([\d.]+)\s*sec\s*([\d.]+)\s*MBytes\s*([\d.]+)\s*Mbits/sec', line)
        if match:
            id, interval_start, interval_end, transfer, bandwidth = match.groups()
            parsed_data.append([i, float(transfer), float(bandwidth)])

    # Create a DataFrame and set column names
    df = pd.DataFrame(parsed_data, columns=['ID', 'Transfer_MBytes', 'Bandwidth_Mbits/sec'])
    
    print(df)
    

def parse_ss_data(file_path : str):

    file_data = None
    regex_data = None

    cwnd_regex = re.compile(r'\bcwnd:(\d+)\b')

    with open(file_path,'r') as file:
        file_data = file.read()

    regex_data = cwnd_regex.findall(file_data)
    
    parsed_data = []
    for i, data_point in enumerate(regex_data):
        parsed_data.append([i, float(data_point)])

    df = pd.DataFrame(parsed_data, columns=['ID', 'Cwnd'])
    print(df)






if __name__ == '__main__':
    parse_ss_data('host-one-ss-out.txt')
    parse_iperf_data('iperf_test_h1-h3_15s.txt')