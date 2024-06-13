from faker import Faker

from faker_cli.templates import CloudFrontLogs, S3AccessLogs


class FakerProvider:
    def __init__(self) -> None:
        self.fake = Faker()
        self.fake.add_provider(S3AccessLogs)
        self.fake.add_provider(CloudFrontLogs)

    def generate_row(self, column_types: list[tuple[str, list]]) -> list[str]:
        return [
            self.fake.format(ctype, *args)
            if not ctype.startswith("unique.")
            else self.fake.unique.format(ctype.removeprefix("unique."), *args)
            for ctype, args in column_types
        ]

    def format(self, log_entry) -> list[str]:
        return self.fake.format(log_entry)
