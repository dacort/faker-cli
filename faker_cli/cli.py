from faker import Faker
import click
import sys
from faker_cli.templates import S3AccessLogs, S3AccessWriter, CloudTrailLogs

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

fake = Faker()
fake.add_provider(S3AccessLogs)
fake.add_provider(CloudTrailLogs)

@click.command()
@click.option("--num-rows", "-n", default=1, help="Number of rows")
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv", help="Format of the output")
@click.option("--columns", "-c", help="Column names", default=None, required=False)
@click.option("--template", "-t", help="Template to use", type=click.Choice(["s3access"]), default=None)
@click.argument("column_types", required=False)
def main(num_rows, format, columns, template, column_types):
    if template:
        writer = S3AccessWriter(sys.stdout, None)
        for i in range(num_rows):
            row = fake.format("s3_access_log")
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

