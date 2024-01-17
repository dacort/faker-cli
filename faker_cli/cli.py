import sys
from typing import List

import click
from faker import Faker

from faker_cli.templates import (
    CloudFrontLogs,
    CloudFrontWriter,
    S3AccessLogs,
    S3AccessWriter,
)
from faker_cli.writer import CSVWriter, JSONWriter


def infer_column_names(col_names, col_types: str) -> List[str]:
    """
    Infer column names from column types
    """
    # For now, nothing special - but eventually we need to parse things out
    if col_names:
        return col_names.split(",")

    return col_types.split(",")


KLAS_MAPPER = {
    "csv": CSVWriter,
    "json": JSONWriter,
}

TEMPLATE_MAPPER = {
    "s3access": [S3AccessWriter, "s3_access_log"],
    "cloudfront": [CloudFrontWriter, "cloudfront_log"],
}

fake = Faker()
fake.add_provider(S3AccessLogs)
fake.add_provider(CloudFrontLogs)


@click.command()
@click.option("--num-rows", "-n", default=1, help="Number of rows")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "deltalake"]),
    default="csv",
    help="Format of the output",
)
@click.option("--output", "-o", type=click.Path(writable=True))
@click.option("--columns", "-c", help="Column names", default=None, required=False)
@click.option("--template", "-t", help="Template to use", type=click.Choice(["s3access", "cloudfront"]), default=None)
@click.argument("column_types", required=False)
def main(num_rows, format, output, columns, template, column_types):
    """
    Generate fake data, easily.

    COLUMN_TYPES is a comma-seperated list of Faker property names, like
    pyint,username,date_this_year

    You can also use --template for real-world synthetic data.
    """
    # Do some initial validation - we must have either template or column tpes
    if not template and not column_types:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
        raise click.BadArgumentUsage("either --template or a list of Faker property names must be provided.")

    # Parquet output requires a filename
    if format in ["parquet", "deltalake"] and output is None:
        raise click.BadArgumentUsage("parquet | deltalake formats requires --output/-o filename parameter.")
    if output is not None and format not in ["parquet", "deltalake"]:
        raise click.BadArgumentUsage("output files not supported for csv/json yet.")

    # Optionally load additional features
    if format == "parquet":
        try:
            from faker_cli.writers.parquet import ParquetWriter

            KLAS_MAPPER["parquet"] = ParquetWriter
        except ImportError:
            raise click.ClickException(
                "Using Parquet writer, but the 'pyarrow' package is not installed. "
                "Make sure to install faker-cli using `pip install faker-cli[parquet]`."
            )

    if format == "deltalake":
        try:
            from faker_cli.writers.delta import DeltaLakeWriter

            KLAS_MAPPER["deltalake"] = DeltaLakeWriter
        except ImportError:
            raise click.ClickException(
                "Using Delta writer, but the 'deltalake' package is not installed. "
                "Make sure to install faker-cli using `pip install faker-cli[delta]`."
            )

    # If the user provides a template, we use that provider and writer and exit.
    # We assume a template has a custom writer that may be different than CSV or JSON
    if template:
        writer = TEMPLATE_MAPPER[template][0](sys.stdout, None)
        log_entry = TEMPLATE_MAPPER[template][1]
        for i in range(num_rows):
            row = fake.format(log_entry)
            writer.write(row)
        return

    # Now, if a template hasn't been provided, generate some fake data!
    col_types = column_types.split(",")
    headers = infer_column_names(columns, column_types)
    writer = KLAS_MAPPER.get(format)(sys.stdout, headers, output)
    for i in range(num_rows):
        # TODO: Handle args
        row = [fake.format(ctype) for ctype in col_types]
        writer.write(row)
    writer.close()
