"""
A template consissts of a combination of a custom output writer format and row format.
"""
from collections import OrderedDict
import string
import random
from typing import Any, Dict, List, Optional
from faker_cli.writer import Writer
from faker.providers import BaseProvider
import datetime as dt


class AWSConstants:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    _http_status_codes: Dict[str, List[int]] = {
        "informational": [100, 101, 102, 103],
        "success": [200, 201, 202, 203, 204, 205, 206, 207, 208, 226],
        "redirection": [300, 301, 302, 303, 304, 305, 306, 307, 308],
        "clientError": [
            400,
            401,
            402,
            403,
            404,
            405,
            406,
            407,
            408,
            409,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            417,
            418,
            421,
            422,
            423,
            424,
            425,
            426,
            428,
            429,
            431,
            451,
        ],
        "serverError": [500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511],
    }

    _key_exchange_algorithms: List[str] = ["RSA", "DH", "ECDH", "DHE", "ECDHE", "PSK"]
    _authentication_algorithms: List[str] = ["RSA", "ECDSA", "DSA"]
    _cipher_algorithms: List[str] = ["AES", "CHACHA20", "Camellia", "ARIA"]
    _mac_algorithms: List[str] = ["SHA", "POLY"]

    _regions: List[str] = [
        "us-east-2",
        "us-east-1",
        "us-west-1",
        "us-west-2",
        "af-south-1",
        "ap-east-1",
        "ap-south-2",
        "ap-southeast-3",
        "ap-southeast-4",
        "ap-south-1",
        "ap-northeast-3",
        "ap-northeast-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-northeast-1",
        "ca-central-1",
        "cn-north-1",
        "cn-northwest-1",
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-south-1",
        "eu-west-3",
        "eu-north-1",
        "eu-south-2",
        "eu-central-2",
        "me-south-1",
        "me-central-1",
        "sa-east-1",
        "us-gov-east-1",
        "us-gov-west-1",
    ]

    _services: List[str] = ["ec2", "cloudtrail", "s3"]


class S3AccessWriter(Writer):
    def __init__(self, output, headers):
        super().__init__(output, headers)

    def write(self, row):
        self.output.write(" ".join(map(str, row)) + "\n")


class AWSProvider(BaseProvider):
    def aws_account_id(self) -> str:
        return "".join(random.choices(string.digits, k=12))

    def aws_arn(
        self,
        partition: Optional[str] = "aws",
        service: Optional[str] = None,
        region: Optional[str] = None,
        account_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> str:
        if not partition:
            partition = self.generator.random_element(elements=["aws", "aws-cn", "aws-us-gov"])
        if not service:
            service = self.generator.random_element(elements=["s3", "ec2", "iam", "sts"])
        if not region and service not in ["iam"]:
            region = self.generator.random_element(elements=AWSConstants._regions)
        if not account_id:
            account_id = self.aws_account_id()

        # TODO: There are a WHOLE bunch more rules here to take care of
        # Also figure out how to handle if resource-type is specificed
        if resource_id is None:
            if service == "iam":
                resource_id = self.generator.random_element(elements=["root", f"user/{self.generator.user_name()}"])
            else:
                resource_id = self.generator.user_name()

        resource_part = resource_id
        if resource_type:
            resource_part = f"{resource_type}/{resource_id}"

        return f"arn:{partition}:{service}:{region or ''}:{account_id}:{resource_part}"

    def aws_iam_arn(self, service: Optional[str] = None, resource: Optional[str] = None) -> str:
        if service is None:
            service = self.generator.random_element(elements=["iam", "sts"])
        if resource is None:
            if service == "iam":
                resource = self.generator.random_element(elements=["root", f"user/{self.generator.user_name()}"])
            if service == "sts":
                resource = self.generator.random_element(
                    elements=[
                        f"federated-user/{self.generator.user_name()}",
                        f"assumed-role/{self.generator.user_name()}/SessionName",
                    ]
                )
        return f"arn:aws:{service}::{self.aws_account_id()}:{resource}"


class S3AccessLogs(AWSProvider):
    __use_weighting__ = True

    def __init__(self, generator: Any):
        super().__init__(generator)

        # Assume a reasonable default for the number of buckets we want to generate logs for
        self.num_buckets = 5
        self.bucket_names = [self.s3_bucket() for _ in range(self.num_buckets)]

        # Problem is, bucket owner should match
        self.num_bucket_owners = 2
        self.bucket_owners = [self.s3_bucket_owner() for _ in range(self.num_bucket_owners)]

        self.bucket_owner_tuples = [
            (self.generator.random_element(elements=self.bucket_owners), name) for name in self.bucket_names
        ]

    def s3_access_log(self) -> List[str]:
        http_method = self.http_method()
        path = self.key()
        bucket_owner, bucket = self.s3_bucket_owner_tuple()
        obj_size = self.object_size()
        total_time = self.total_time()
        return [
            bucket_owner,
            bucket,
            self.time(),
            self.remote_ip(),
            self.requestor(),
            path,
            self.request_uri(http_method, path),
            self.http_status(),
            self.error_code(),
            self.bytes_sent(total_object_size=obj_size),
            obj_size,
            total_time,
            self.turnaround_time(total_time),
            self.referer(),
            self.s3_user_agent(),
            self.version_id(),
            self.host_id(),
            self.sig_version(),
            self.cipher_suite(),
            self.authentication_type(),
            self.host_header(),
            self.tls_version(),
            self.access_point_arn(),
            self.acl_required(),
        ]

    def _random_alnum(
        self,
        length: int = 64,
        elements: Optional[List[str]] = [string.ascii_lowercase, string.digits],
    ) -> str:
        return "".join(random.choices("".join(elements), k=length))

    def s3_bucket_owner(self) -> str:
        return self._random_alnum(64)

    def s3_bucket(self) -> str:
        # return self.generator.random_element(elements=self.bucket_names)
        return self.generator.domain_word()

    def s3_bucket_owner_tuple(self) -> str:
        return self.generator.random_element(elements=self.bucket_owner_tuples)

    def time(self) -> str:
        return self.generator.date_time(tzinfo=dt.timezone.utc).strftime("[%d/%b/%Y:%H:%M:%S %z]")

    def remote_ip(self) -> str:
        return self.generator.ipv4_public()

    def requestor(self) -> str:
        """
        One of the following:
            - A canonical user ID like bucket_owner
            - - for unauthenticated requests
            - An IAM user ARN
        """
        return self.generator.random_element(
            elements=(
                self._random_alnum(64),
                "-",
                self.generator.aws_iam_arn(),
            )
        )

    def operation(self) -> str:
        """
        The operation listed here is declared as SOAP.operation,
        REST.HTTP_method.resource_type,WEBSITE.HTTP_method.resource_type,
        or BATCH.DELETE.OBJECT, or S3.action.resource_type for Lifecycle and logging.
        """
        # TODO: Figure out what SOAP operations, and REST/WEBSITE resource_types to use
        resource_type = self.generator.random_element(elements=("OBJECT", "OBJECT_GET"))
        return self.generator.random_element(
            elements=OrderedDict(
                [
                    ("SOAP.operation", 0.1),
                    (f"REST.{self.http_method()}.{resource_type}", 0.6),
                    (f"WEBSITE.{self.http_method()}.{resource_type}", 0.1),
                    ("BATCH.DELETE.OBJECT", 0.1),
                    (
                        self.generator.random_element(
                            elements=(
                                "S3.EXPIRE.OBJECT",
                                "S3.CREATE.DELETEMARKER",
                                "S3.TRANSITION_SIA.OBJECT",
                                "S3.TRANSITION_ZIA.OBJECT",
                                "S3.TRANSITION_INT.OBJECT",
                                "S3.TRANSITION_GIR.OBJECT",
                                "S3.TRANSITION.OBJECT",
                                "S3.TRANSITION_GDA.OBJECT",
                                "S3.DELETE.UPLOAD",
                            )
                        ),
                        0.1,
                    ),
                ]
            )
        )

    def request_id(self) -> str:
        # 3E57427F33A59F07
        return self._random_alnum(16, [string.ascii_uppercase, string.digits])

    def http_method(self) -> str:
        return self.generator.random_element(elements=("GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"))

    def key(self) -> str:
        return self.generator.file_path()

    def request_uri(self, method: Optional[str] = None, key: Optional[str] = None) -> str:
        if method is None:
            method = self.http_method()
        if key is None:
            key = self.key()

        # https://almanac.httparchive.org/en/2020/http
        http_version = self.generator.random_element(
            elements=OrderedDict(
                [
                    ("0.9", 0.01),
                    ("1.0", 0.05),
                    ("1.1", 0.3),
                    ("2.0", 0.64),
                ]
            )
        )
        return f'"{method} {key} HTTP/{http_version}"'

    def http_status(self) -> str:
        return str(self._http_status_code())

    def error_code(self) -> str:
        return self.generator.random_element(elements=("NoSuchBucket", "NoSuchLifecycleConfiguration", "-"))

    def bytes_sent(self, total_object_size: Optional[int] = None) -> str:
        return self.generator.random_element(
            elements=(
                "-",
                self.generator.pyint(min_value=1, max_value=total_object_size or (1024 * 1024 * 1024)),
            )
        )

    def object_size(self) -> str:
        return self.generator.pyint(min_value=1, max_value=1024 * 1024 * 1024)

    def total_time(self) -> str:
        """
        The number of milliseconds that the request was in flight
        from the server's perspective.
        """
        return self.generator.pyint(min_value=1, max_value=1000)

    def turnaround_time(self, total_time: Optional[int] = None) -> str:
        """
        The number of milliseconds that Amazon S3 spent processing your request.
        """
        return self.generator.pyint(min_value=1, max_value=total_time or 1000)

    def referer(self) -> str:
        return self.generator.random_element(elements=("-", self.generator.uri()))

    def s3_user_agent(self) -> str:
        return f'"{self.generator.user_agent()}"'

    def version_id(self) -> str:
        """
        3HL4kqtJvjVBH40Nrjfkd
        """
        return self.generator.random_element(
            elements=OrderedDict(
                [
                    ("-", 0.1),
                    (
                        self._random_alnum(21, [string.ascii_letters, string.digits]),
                        0.9,
                    ),
                ]
            )
        )

    def host_id(self) -> str:
        return self._random_alnum(
            self.generator.pyint(min_value=10, max_value=128),
            [string.ascii_letters, string.digits, "/=+"],
        )

    def sig_version(self) -> str:
        return self.generator.random_element(elements=("SigV2", "SigV4", "-"))

    def cipher_suite(self, is_https: Optional[bool] = True):
        if not is_https:
            return "-"

        # TODO: Make this somewhat more realistic
        return "-".join(
            [
                self.generator.random_element(AWSConstants._key_exchange_algorithms),
                self.generator.random_element(AWSConstants._authentication_algorithms),
                self.generator.random_element(AWSConstants._cipher_algorithms)
                + self.generator.random_element(elements=("128", "256")),
                self.generator.random_element(AWSConstants._mac_algorithms)
                + self.generator.random_element(elements=("128", "256")),
            ]
        )

    def authentication_type(self) -> str:
        return self.generator.random_element(elements=("AuthHeader", "QueryString" "-"))

    def host_header(self) -> str:
        # TODO: use correct endpoints as defined in https://docs.aws.amazon.com/general/latest/gr/s3.html
        # This might also be <bucket_name>.s3.us-east-1.amazonaws.com
        return f"s3.{self.generator.random_element(AWSConstants._regions)}.amazonaws.com"

    def tls_version(self) -> str:
        return self.generator.random_element(elements=("TLSv1.1", "TLSv1.2", "TLSv1.3", "-"))

    def access_point_arn(self) -> str:
        return self.aws_arn(service="s3", resource_type="accesspoint")

    def acl_required(self) -> str:
        return self.generator.random_element(elements=("Yes", "-"))

    def _http_status_code(self, response_type: Optional[str] = None) -> int:
        status_codes = None
        if response_type is not None:
            status_codes = AWSConstants._http_status_codes.get(response_type)
        else:
            status_codes = [num for sublist in AWSConstants._http_status_codes.values() for num in sublist]

        return self.generator.random_element(elements=status_codes)


# then add new provider to faker instance
# fake.add_provider(S3AccessLogs)


class CloudTrailLogs(AWSProvider):
    def event_version(self) -> str:
        return "1.0"

    def event_time(self) -> str:
        return self.generator.iso8601()

    def event_source(self) -> str:
        return self.generator.random_element(AWSConstants._services) + ".amazonaws.com"

    def user_id_with_iam_user(self) -> str:
        """
        "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAJ45Q7YFFAREXAMPLE",
        "arn": "arn:aws:iam::123456789012:user/Alice",
        "accountId": "123456789012",
        "accessKeyId": "",
        "userName": "Alice"
        }
        """
        return {
            "type": "IAMUser",
            "principalId": "AIDAJ45Q7YFFAREXAMPLE",
            "arn": self.aws_arn(service="iam", resource_type="user"),
            "accountId": self.aws_account_id(),
        }
