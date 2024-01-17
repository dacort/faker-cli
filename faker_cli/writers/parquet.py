
import pyarrow as pa
import pyarrow.parquet as pq

from faker_cli.writer import Writer

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