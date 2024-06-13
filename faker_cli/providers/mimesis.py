from mimesis import Field


class MimesisProvider:
    def __init__(self) -> None:
        self.field = Field()

    def generate_row(self, column_types: list[tuple[str, list]]) -> list[str]:
        return [self.field._lookup_method(ctype)(*args) for ctype, args in column_types]

    def format(self, log_entry) -> list[str]:
        raise NotImplementedError


# field("person.username", mask="U_d", drange=(100, 1000))
