# Faker CLI

[Faker](https://faker.readthedocs.io/en/master/) is an awesome Python library, but I often just want a simple command I can run to generate data in a variety of formats.

With Faker CLI, you can easily generate CSV, JSON, or Parquet data with fields of your choosing.

You can also utilize pre-built templates for common data formats!

## Installation

```bash
pip install faker-cli
```

> [!TIP]
> To use Parquet or Delta Lake, use `pip install faker-cli[parquet]` or `pip install faker-cli[delta]`

## Usage

Once installed you should have the `fake` command in your path. Run the following see usage / help:

```bash
fake --help
```

By default, `fake` will generate a CSV output for you. You just specify the number of rows you want and the column types.

```bash
fake -n 10 pyint,user_name,date_this_year
```

BAM! You've got a CSV file with your data.

```
pyint,user_name,date_this_year
8649,fward,2023-03-08
3933,zharris,2023-03-20
1469,jasonellis,2023-05-16
3660,heather91,2023-02-10
9160,cameronlopez,2023-05-05
2735,candacemoore,2023-05-12
7240,zachary06,2023-01-23
9778,thomasstacey,2023-05-23
5820,kenneth36,2023-04-26
2856,michael23,2023-01-16
```

### JSON

Wnat a JSON file? Sweet, use `-f json`.

```bash
fake -n 10 pyint,user_name,date_this_year -f json
```

```json
{"pyint": 3854, "user_name": "cchavez", "date_this_year": "2023-01-20"}
{"pyint": 2008, "user_name": "vnguyen", "date_this_year": "2023-04-03"}
{"pyint": 1434, "user_name": "karen38", "date_this_year": "2023-03-02"}
{"pyint": 4922, "user_name": "duncanellen", "date_this_year": "2023-04-22"}
{"pyint": 230, "user_name": "tiffany72", "date_this_year": "2023-02-25"}
{"pyint": 7252, "user_name": "maydouglas", "date_this_year": "2023-04-01"}
{"pyint": 2716, "user_name": "sheilaflores", "date_this_year": "2023-03-20"}
{"pyint": 2827, "user_name": "parksandra", "date_this_year": "2023-04-01"}
{"pyint": 3353, "user_name": "melissaatkinson", "date_this_year": "2023-02-10"}
{"pyint": 5306, "user_name": "mark12", "date_this_year": "2023-04-16"}
```

### Column Names

Default column names aren't good enough for you? Fine, use your own.

```bash
fake -n 10 pyint,user_name,date_this_year -f json -c id,awesome_name,last_attention_at
```

```
{"id": 6048, "awesome_name": "jtran", "last_attention_at": "2023-04-24"}
{"id": 4310, "awesome_name": "stacey99", "last_attention_at": "2023-04-27"}
{"id": 1839, "awesome_name": "jho", "last_attention_at": "2023-03-07"}
{"id": 236, "awesome_name": "melissamassey", "last_attention_at": "2023-04-17"}
{"id": 6599, "awesome_name": "mwells", "last_attention_at": "2023-04-25"}
{"id": 6071, "awesome_name": "wilcoxrick", "last_attention_at": "2023-01-17"}
{"id": 9646, "awesome_name": "michael92", "last_attention_at": "2023-04-22"}
{"id": 6986, "awesome_name": "ballen", "last_attention_at": "2023-01-08"}
{"id": 6892, "awesome_name": "jennifer61", "last_attention_at": "2023-01-03"}
{"id": 1967, "awesome_name": "jmendoza", "last_attention_at": "2023-01-23"}
```

### Providers (beta)

While [Faker](https://faker.readthedocs.io) is a sweet library, we all like options don't we? [Mimesis](https://mimesis.name/en/master/) is _also_ awesome and can be quite a bit faster than Faker. 🤫 You can use a different provider by using `-p mimesis`.

> [!NOTE]  
> Providers use their own syntax for data types, so you must change out your column names as necessary.

To generate the same dataset above with Mimesis for example:

```bash
fake -p mimesis -n 10 "numeric.integer_number(0),person.username,datetime.date(2024)" -f json -c id,awesome_name,last_attention_at
```

### Provider Arguments

Some [Faker providers](https://faker.readthedocs.io/en/master/providers/baseprovider.html) (like `pyint`) take arguments. You can also specify those if you like, separated by semi-colons (_because some arguments take a comma-separated string :)_)

```bash
fake -n 10 "pyint(1;100),credit_card_number(amex),pystr_format(?#-####)" -f json -c id,credit_card_number,license_plate
```

> [!IMPORTANT]
> When using arguments with output formats like JSON, it's best to provide column headers as well with `-c`.

And unique values are supported as well.

```bash
fake -n 10 "unique.pyint(1;10),unique.name"
```

### Parquet

OK, it had to happen, you can even write Parquet.

Install with the `parquet` module: `pip install faker-cli[parquet]`

```bash
fake -n 10 pyint,user_name,date_this_year -f parquet -o sample.parquet
```

_youcanevenwritestraighttos3_ 🤭

```bash
fake -n 10 pyint,user_name,date_this_year -f parquet -o s3://YOUR_BUCKET/data/sample.parquet
```

### Delta Lake

Data can be exported as a delta lake table.

Install with the `delta` module: `pip install faker-cli[delta]`

```bash
fake -n 10 pyint,user_name,date_this_year -f deltalake -o sample_data
```

### Iceberg

And, of course, Iceberg tables!

Currently supported are writing to a Glue or generic SQL catalog.

Install with the `iceberg` module: `pip install faker-cli[iceberg]`

```bash
fake -n 10 pyint,user_name,date_this_year -f iceberg -C glue://default.iceberg_sample -o s3://YOUR_BUCKET/iceberg-data/
```

## Templates

The libary includes a couple templates that can be used to generate certain types of fake data easier.

Today, the only templates that exist are for S3 Access and CloudFront logs.

Want to generate 1 MILLION S3 Access logs in ~2 minutes? Now you can. (But I only show 10 below so as not to crash your terminal)

```bash
fake -t s3access -n 10
```

How about CloudFront? Go ahead.

```bash
fake -t cloudfront -n 10
```

> **Warning**: Both of these templates are still being validated - please be cautious!
