import csv
import json

class Writer:
    def __init__(self, output, headers):
        self.output = output
        self.headers = headers
        self.writer = None

    def write(self, row):
        pass
    
    def close(self):
        self.writer.close()

class CSVWriter(Writer):
    def __init__(self, output, headers):
        super().__init__(output, headers)
        self.writer = csv.writer(self.output)
        self.write(headers)

    def write(self, row):
        self.writer.writerow(row)

class JSONWriter(Writer):
    def __init__(self, output, headers):
        super().__init__(output, headers)
        self.writer = self.output

    def write(self, row):
        jsonl = json.dumps(dict(zip(self.headers, row)), default=str)
        self.writer.write(jsonl)
        self.writer.write('\n')