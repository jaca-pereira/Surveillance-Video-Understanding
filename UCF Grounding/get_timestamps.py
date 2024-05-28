import json
import csv

def process_timestamps(json_list):
    results = []
    for entry in json_list:
        video_name = entry.key()
        start_time = entry['timestamps'][0][0]
        end_time = entry['timestamps'][-1][-1]
        results.append((video_name, start_time, end_time))
    return results

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['video_name', 'start', 'end'])  # Header row
        for result in results:
            csvwriter.writerow(result)

def main():
    files = ['UCFCrime_Train.json', 'UCFCrime_Val.json', 'UCFCrime_Test.json']

    for file_path in files:
        json_data = load_json(file_path)
        results = process_timestamps(json_data)
        write_to_csv(results, f'{file_path.removesuffix(".json")}.csv')

if __name__ == "__main__":
    main()

