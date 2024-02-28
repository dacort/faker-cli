from tempfile import TemporaryDirectory

import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog

from faker_cli.writer import Writer
from faker_cli.writers.parquet import ParquetWriter


class IcebergWriter(ParquetWriter):
    def __init__(self, output, headers, filename):
        super().__init__(output, headers, filename)
        self.warehouse_path = filename
        self.temp_path = TemporaryDirectory()
        self.table: pa.Table = None
        self.catalog: SqlCatalog = SqlCatalog(
            "default",
            **{
                "uri": f"sqlite:////{self.temp_path.name}/pyiceberg_catalog.db",
                "warehouse": self.warehouse_path,
            },
        )

    # def write(self, row):
    #     df = pa.Table.from_pylist([dict(zip(self.headers, row))])
    #     if self.table is None:
    #         self.table = self._init_table("test", df.schema)

    #     # Kind of works, but writes a file per row
    #     self.table.append(df)

    def _init_table(self, name, schema):
        self.catalog.create_namespace("default")

        table = self.catalog.create_table(
            f"default.{name}",
            schema=schema,
        )

        return table

    def close(self):
        iceberg_table = self._init_table("test", self.table.schema)
        iceberg_table.overwrite(self.table)
        
        pa.fs.copy_files(f"{self.temp_path.name}/pyiceberg_catalog.db", f"{self.warehouse_path}pyiceberg_catalog.db")
        return super().close()
