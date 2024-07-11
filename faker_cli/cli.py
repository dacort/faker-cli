import sys

import click
from faker import Faker

from faker_cli.parser import infer_column_names, parse_column_types
from faker_cli.providers.faker import FakerProvider
from faker_cli.providers.mimesis import MimesisProvider
from faker_cli.templates import CloudFrontWriter, S3AccessWriter
from faker_cli.writer import CSVWriter, JSONWriter

KLAS_MAPPER = {
    "csv": CSVWriter,
    "json": JSONWriter,
}

TEMPLATE_MAPPER = {
    "s3access": [S3AccessWriter, "s3_access_log"],
    "cloudfront": [CloudFrontWriter, "cloudfront_log"],
}


@click.command()
@click.option("--num-rows", "-n", default=1, help="Number of rows")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "parquet", "deltalake", "iceberg"]),
    default="csv",
    help="Format of the output",
)
@click.option("--output", "-o", type=click.Path(writable=True))
@click.option("--columns", "-c", help="Column names", default=None, required=False)
@click.option("--template", "-t", help="Template to use", type=click.Choice(["s3access", "cloudfront"]), default=None)
@click.option("--catalog", "-C", help="Catalog URI", default=None, required=False)
@click.argument("column_types", required=False)
@click.option("--provider", "-p", help="Fake data provider", type=click.Choice(["faker", "mimesis"]), default="faker")
def main(num_rows, format, output, columns, template, catalog, column_types, provider):
    """
    Generate fake data, easily.

    COLUMN_TYPES is a comma-seperated list of Faker property names, like
    pyint,user_name,date_this_year

    You can also use --template for real-world synthetic data.
    """
    if provider == "faker":
        fake = FakerProvider()
    elif provider == "mimesis":
        fake = MimesisProvider()
    else:
        pass

    # Do some initial validation - we must have either template or column tpes
    if not template and not column_types:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
        raise click.BadArgumentUsage("either --template or a list of Faker property names must be provided.")

    # Templates are only supported with Faker at the moment
    if template and provider != "faker":
        raise click.BadArgumentUsage('templates are only supported with the "faker" provider.')

    # Parquet output requires a filename
    if format in ["parquet", "deltalake", "iceberg"] and output is None:
        raise click.BadArgumentUsage(f"{format} format requires --output/-o filename parameter.")
    if output is not None and format not in ["parquet", "deltalake", "iceberg"]:
        raise click.BadArgumentUsage("output files not supported for csv/json yet.")
    if catalog and format not in ['iceberg']:
        raise click.BadArgumentUsage("catalog option is only available for Iceberg formats")

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

    if format == "iceberg":
        try:
            from faker_cli.writers.iceberg import IcebergWriter

            KLAS_MAPPER["iceberg"] = IcebergWriter
        except ImportError:
            raise click.ClickException(
                "Using Iceberg writer, but the 'iceberg' package is not installed. "
                "Make sure to install faker-cli using `pip install faker-cli[iceberg]`."
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
    # col_types = column_types.split(",")
    # Note that if args are provided, the column headers are less than ideal
    col_types = parse_column_types(column_types)
    headers = infer_column_names(columns, column_types)
    format_klas = KLAS_MAPPER.get(format)
    if format_klas is None:
        raise click.ClickException(f"Format {format} not supported.")
    # Fix in a better way - maybe passing **kwargs?
    writer = format_klas(sys.stdout, headers, output, catalog)
    for i in range(num_rows):
        writer.write(fake.generate_row(col_types))
    writer.close()


def generate_row(fake: Faker, column_types: list[tuple[str, list]]) -> list[str]:
    return [
        fake.format(ctype, *args)
        if not ctype.startswith("unique.")
        else fake.unique.format(ctype.removeprefix("unique."), *args)
        for ctype, args in column_types
    ]
