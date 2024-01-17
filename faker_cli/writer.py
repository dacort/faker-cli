import csv
import json
from typing import Optional


class Writer:
    def __init__(self, output, headers, filename: Optional[str] = None):
        self.output = output
        self.headers = headers
        self.writer = None

    def write(self, row):
        pass

    def close(self):
        pass


class CSVWriter(Writer):
    def __init__(self, output, headers, filename):
        super().__init__(output, headers)
        self.writer = csv.writer(self.output)
        self.write(headers)

    def write(self, row):
        self.writer.writerow(row)


class JSONWriter(Writer):
    def __init__(self, output, headers, filename):
        super().__init__(output, headers)
        self.writer = self.output

    def write(self, row):
        jsonl = json.dumps(dict(zip(self.headers, row)), default=str)
        self.writer.write(jsonl)
        self.writer.write("\n")
