import csv
import json
from typing import Optional
import pyarrow as pa
import pyarrow.parquet as pq


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


class ParquetWriter(Writer):
    def __init__(self, output, headers, filename):
        super().__init__(output, headers)
        self.filename = filename
        self.table: pa.Table = None

    def write(self, row):
        ini_dict = [{k: [v]} for k, v in list(zip(self.headers, row))]
        tbl = {k: v for d in ini_dict for k, v in d.items()}
        table = pa.table(tbl)
        if self.table is None:
            self.table = table
        else:
            self.table = pa.concat_tables([self.table, table])

    def close(self):
        pq.write_table(self.table, self.filename)
