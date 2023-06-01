from faker import Faker
import click
import sys
from faker_cli.templates import CloudFrontWriter, S3AccessLogs, S3AccessWriter, CloudTrailLogs, CloudFrontLogs

from faker_cli.writer import CSVWriter, JSONWriter
from typing import List

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
    "json": JSONWriter
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
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv", help="Format of the output")
@click.option("--columns", "-c", help="Column names", default=None, required=False)
@click.option("--template", "-t", help="Template to use", type=click.Choice(["s3access", "cloudfront"]), default=None)
@click.argument("column_types", required=False)
def main(num_rows, format, columns, template, column_types):
    """
    Generate fake data, easily.

    COLUMN_TYPES is a comma-seperated list of Faker property names, like
    pyint,username,date_this_year

    You can also use --template for real-world synthetic data.
    """
    if not template and not column_types:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
        raise click.BadArgumentUsage(
            "either --template or a list of Faker property names must be provided."
        )
    if template:
        writer = TEMPLATE_MAPPER[template][0](sys.stdout, None)
        log_entry = TEMPLATE_MAPPER[template][1]
        for i in range(num_rows):
            row = fake.format(log_entry)
            writer.write(row)
        return
        
    col_types = column_types.split(",")
    headers = infer_column_names(columns, column_types)
    writer = KLAS_MAPPER.get(format)(sys.stdout, headers)
    for i in range(num_rows):
        # TODO: Handle args
        row = [ fake.format(ctype) for ctype in col_types ]
        writer.write(row)
    # Convert columns to templates
    # if format == "csv":
    #     column_types = [f"{{{{{x}}}}}" for x in column_types.split(',')]
    #     print(fake.csv(data_columns=(column_types), num_rows=num_rows))
    # elif format == "json":
    #     # convert column_types into a dict
    #     cols = column_types.split(",")
    #     column_def = dict(zip(cols, cols))
    #     print(fake.json(data_columns=column_def, num_rows=num_rows))

