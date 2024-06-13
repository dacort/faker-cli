from tempfile import TemporaryDirectory
from urllib.parse import urlparse

import click
import pyarrow as pa
from pyiceberg.catalog import Catalog
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.exceptions import NoSuchNamespaceError

from faker_cli.writer import Writer
from faker_cli.writers.parquet import ParquetWriter


class CatalogManager:
    def __init__(self, uri: str, location: str) -> None:
        self.catalog = self._from_uri(uri, location)

    def _from_uri(self, uri: str, location:str) -> Catalog:
        u = urlparse(uri)
        namespace = u.netloc.split(".")[0]
        if u.scheme == "glue":
            try:
                from pyiceberg.catalog.glue import GlueCatalog
            except ImportError:
                raise click.ClickException(
                    "Using Iceberg writer with Glue catalog, but the 'boto3' package is not installed. "
                    "Make sure to install faker-cli using `pip install faker-cli[iceberg,glue]`."
                )
            glue = GlueCatalog(namespace)
            try:
                glue.load_namespace_properties(namespace)
            except NoSuchNamespaceError:
                glue.create_namespace(namespace)
            return glue

        elif u.scheme == "sqlite":
            self.temp_path = TemporaryDirectory()
            sql = SqlCatalog(
                namespace, uri=f"sqlite:////{self.temp_path.name}/pyiceberg_catalog.db", warehouse=location
            )
            sql.create_namespace(namespace)
            return sql
        else:
            raise Exception("Unknown catalog type")


class IcebergWriter(ParquetWriter):
    def __init__(self, output, headers, filename, catalog_uri):
        super().__init__(output, headers, filename)
        self.warehouse_path = filename
        self.temp_path = TemporaryDirectory()
        self.table: pa.Table = None
        self.catalog: CatalogManager = CatalogManager(catalog_uri, filename)

    # def write(self, row):
    #     df = pa.Table.from_pylist([dict(zip(self.headers, row))])
    #     if self.table is None:
    #         self.table = self._init_table("test", df.schema)

    #     # Kind of works, but writes a file per row
    #     self.table.append(df)

    def _init_table(self, name, schema):
        # self.catalog.create_namespace("default")

        table = self.catalog.catalog.create_table(
            f"default.{name}",
            schema=schema,
        )

        return table

    def close(self):
        iceberg_table = self._init_table("test", self.table.schema)
        iceberg_table.overwrite(self.table)

        pa.fs.copy_files(f"{self.temp_path.name}/pyiceberg_catalog.db", f"{self.warehouse_path}pyiceberg_catalog.db")
        return super().close()
        return super().close()
