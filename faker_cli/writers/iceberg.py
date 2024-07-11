from tempfile import TemporaryDirectory
from urllib.parse import urlparse

import click
import pyarrow as pa
from pyiceberg.catalog import Catalog
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.exceptions import NoSuchNamespaceError, NoSuchTableError

from faker_cli.writers.parquet import ParquetWriter


class CatalogManager:
    def __init__(self, uri: str, location: str) -> None:
        [self.database, self.table] = urlparse(uri).netloc.split(".")
        self.catalog = self._from_uri(uri, location)

    def _from_uri(self, uri: str, location: str) -> Catalog:
        u = urlparse(uri)
        if u.scheme == "glue":
            try:
                from pyiceberg.catalog.glue import GlueCatalog
            except ImportError:
                raise click.ClickException(
                    "Using Iceberg writer with Glue catalog, but the 'boto3' package is not installed. "
                    "Make sure to install faker-cli using `pip install faker-cli[iceberg,glue]`."
                )
            glue = GlueCatalog(self.database)
            try:
                glue.load_namespace_properties(self.database)
                glue.load_table(u.netloc)
                raise Exception("Table already exists, please delete or choose another name.")
            except NoSuchNamespaceError:
                glue.create_namespace(self.database)
            except NoSuchTableError:
                pass

            return glue

        elif u.scheme == "sqlite":
            self.temp_path = TemporaryDirectory()
            sql = SqlCatalog(
                self.database, uri=f"sqlite:////{self.temp_path.name}/pyiceberg_catalog.db", warehouse=location
            )
            sql.create_namespace(self.database)
            return sql
        else:
            raise Exception("Unsupported catalog type, only glue or sqllite are supported.")

    def create_table(self, schema, warehouse_path) -> pa.Table:
        if self.catalog is SqlCatalog:
            table = self.catalog.create_table(
                f"{self.database}.{self.table}",
                schema=schema,
            )
        else:
            # location required for GlueCatalog
            table = self.catalog.create_table(
                f"{self.database}.{self.table}",
                schema=schema,
                location=warehouse_path.rstrip("/"),
            )
        return table


class IcebergWriter(ParquetWriter):
    def __init__(self, output, headers, filename, catalog_uri):
        super().__init__(output, headers, filename, catalog_uri)
        self.warehouse_path = filename
        self.temp_path = TemporaryDirectory()
        self.table: pa.Table = None
        self.catalog: CatalogManager = CatalogManager(catalog_uri, filename)

    def close(self):
        iceberg_table = self.catalog.create_table(self.table.schema, self.warehouse_path)
        iceberg_table.overwrite(self.table)

        if self.catalog is SqlCatalog:
            pa.fs.copy_files(
                f"{self.temp_path.name}/pyiceberg_catalog.db", f"{self.warehouse_path}pyiceberg_catalog.db"
            )
        return super().close()
