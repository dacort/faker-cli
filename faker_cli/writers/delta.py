import deltalake

from faker_cli.writers.parquet import ParquetWriter


class DeltaLakeWriter(ParquetWriter):
    def close(self):
        deltalake.write_deltalake(table_or_uri=self.filename, data=self.table)
