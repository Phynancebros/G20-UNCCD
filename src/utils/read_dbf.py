from dbfread import DBF
import csv
import sys

def read_dbf(file_path):
    """
    Reads a DBF file and saves its contents to a CSV file.
    
    Parameters:
    - file_path: Path to the DBF file.
    """
    try:
        table = DBF(file_path, encoding='latin1')
        csv_path = file_path.replace('.dbf', '.csv')
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(table.field_names)
            for record in table:
                writer.writerow(list(record.values()))
        print(f"Saved attribute data to {csv_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_dbf.py <path_to_dbf_file>")
    else:
        read_dbf(sys.argv[1])
