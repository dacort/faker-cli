"""
A template consissts of a combination of a custom output writer format and row format.
"""
from collections import OrderedDict
import string
import random
from typing import Any, Dict, List, Optional, Tuple
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

    # Generated from github.com/tobilg/aws-edge-lcoations
    # curl -L "https://github.com/tobilg/aws-edge-locations/raw/master/dist/aws-edge-locations.json" | \
    # jq -r 'keys[] as $k | "(\"\($k)\", \(.[$k] | .count)),"'  | pbcopy
    _cloudfront_edge_locations: List[Tuple[str, int]] = [
        ("AKL", 2),
        ("AMS", 5),
        ("ARN", 4),
        ("ATH", 1),
        ("ATL", 17),
        ("BAH", 2),
        ("BCN", 2),
        ("BKK", 2),
        ("BLR", 5),
        ("BNA", 2),
        ("BOG", 3),
        ("BOM", 8),
        ("BOS", 5),
        ("BRU", 1),
        ("BUD", 1),
        ("CCU", 2),
        ("CDG", 11),
        ("CGK", 5),
        ("CMH", 1),
        ("CPH", 3),
        ("CPT", 1),
        ("DEL", 14),
        ("DEN", 6),
        ("DFW", 18),
        ("DTW", 2),
        ("DUB", 2),
        ("DUS", 3),
        ("DXB", 1),
        ("EWR", 10),
        ("EZE", 2),
        ("FCO", 6),
        ("FJR", 3),
        ("FOR", 4),
        ("FRA", 17),
        ("GIG", 5),
        ("GRU", 8),
        ("HAM", 6),
        ("HAN", 1),
        ("HEL", 4),
        ("HIO", 1),
        ("HKG", 4),
        ("HYD", 5),
        ("IAD", 20),
        ("IAH", 6),
        ("ICN", 8),
        ("JFK", 8),
        ("JNB", 1),
        ("KIX", 5),
        ("KUL", 2),
        ("LAX", 15),
        ("LHR", 25),
        ("LIM", 2),
        ("LIS", 1),
        ("MAA", 8),
        ("MAD", 10),
        ("MAN", 5),
        ("MCI", 2),
        ("MCT", 1),
        ("MEL", 3),
        ("MIA", 11),
        ("MNL", 1),
        ("MRS", 6),
        ("MSP", 4),
        ("MUC", 4),
        ("MXP", 9),
        ("NBO", 1),
        ("NRT", 22),
        ("ORD", 20),
        ("OSL", 2),
        ("OTP", 1),
        ("PDX", 2),
        ("PEK", 1),
        ("PER", 1),
        ("PHL", 2),
        ("PHX", 3),
        ("PMO", 1),
        ("PNQ", 1),
        ("PRG", 1),
        ("PVG", 1),
        ("QRO", 1),
        ("SCL", 3),
        ("SEA", 6),
        ("SFO", 8),
        ("SGN", 1),
        ("SIN", 7),
        ("SLC", 1),
        ("SOF", 1),
        ("SYD", 4),
        ("SZX", 1),
        ("TLV", 2),
        ("TPA", 1),
        ("TPE", 3),
        ("TXL", 5),
        ("VIE", 3),
        ("WAW", 3),
        ("ZAG", 1),
        ("ZHY", 1),
        ("ZRH", 2),
    ]


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
        """
        Build an ARN for either a random service or provided.
        Reference: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html
        """
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
        """
        Generate an IAM or STS ARN
        """
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

    def _random_alnum(
        self,
        length: int = 64,
        elements: Optional[List[str]] = [string.ascii_lowercase, string.digits],
    ) -> str:
        return "".join(random.choices("".join(elements), k=length))

    def _http_status_code(self, response_type: Optional[str] = None) -> int:
        status_codes = None
        if response_type is not None:
            status_codes = AWSConstants._http_status_codes.get(response_type)
        else:
            status_codes = [num for sublist in AWSConstants._http_status_codes.values() for num in sublist]

        return self.generator.random_element(elements=status_codes)


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
            self.s3a_time(),
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

    def s3_bucket_owner(self) -> str:
        return self._random_alnum(64)

    def s3_bucket(self) -> str:
        # return self.generator.random_element(elements=self.bucket_names)
        # TODO: S3 Buckets should be globally unique
        return self.generator.domain_word()

    def s3_bucket_owner_tuple(self) -> str:
        return self.generator.random_element(elements=self.bucket_owner_tuples)

    def s3a_time(self) -> str:
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


class CloudTrailLogs(AWSProvider):
    """
    There are CloudTrail management events and CloudTrail data events.
    There is a page [here](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-events-with-cloudtrail.html)
    that has more detail about what each of those are, but in short management events are control plane operations and 
    data events are operations on specific resources. 
    Alas, there's no easy way to generate realistic fake versions of these without serious time-consuming work.
    - CloudTrail list of service topics for each AWS service: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-aws-service-specific-topics.html
    - Table of data events: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html
    - Example of S3 data event: https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html#cloudtrail-object-level-tracking
    """
    __use_weighting__ = True

    def event_version(self) -> str:
        return "1.08"

    def event_time(self) -> str:
        return self.generator.iso8601()

    def event_source(self) -> str:
        return self.generator.random_element(AWSConstants._services) + ".amazonaws.com"

    def user_id_with_iam_user(self) -> str:
        """
        https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html#cloudtrail-event-reference-user-identity-examples
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAJ45Q7YFFAREXAMPLE",
            "arn": "arn:aws:iam::123456789012:user/Alice",
            "accountId": "123456789012",
            "accessKeyId": "",
            "userName": "Alice"
        }
        """
        username = self.generator.user_name()
        accountid = self.aws_account_id()
        return {
            "type": "IAMUser",
            "principalId": "AIDAJ45Q7YFFAREXAMPLE",
            "arn": self.aws_arn(service="iam", account_id=accountid, resource_type="user", resource_id=username),
            "accountId": accountid,
            "accessKeyId": "",
            "userName": username,
        }

class CloudFrontWriter(Writer):
    def __init__(self, output, headers):
        super().__init__(output, headers)
        self.output.write("#Version: 1.0\n")
        self.output.write("#Fields: date time x-edge-location sc-bytes c-ip cs-method cs(Host) cs-uri-stem sc-status cs(Referer) cs(User-Agent) cs-uri-query cs(Cookie) x-edge-result-type x-edge-request-id x-host-header cs-protocol cs-bytes time-taken x-forwarded-for ssl-protocol ssl-cipher x-edge-response-result-type cs-protocol-version fle-status fle-encrypted-fields c-port time-to-first-byte x-edge-detailed-result-type sc-content-type sc-content-len sc-range-start sc-range-end\n")

    def write(self, row):
        self.output.write("\t".join(map(str, row)) + "\n")

class CloudFrontLogs(AWSProvider):
    __use_weighting__ = True
    """
    https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html#LogFileFormat
    """

    def cloudfront_log(self) -> List[str]:
        return [
            self.cf_date(),
            self.cf_time(),
            self.edge_location(),
            self.sc_bytes(),
            self.c_ip(),
            self.cs_method(),
            self.cs_host(),
            self.cs_uri_stem(),
            self.sc_status(),
            self.referer_domain(),
            self.generator.user_agent(),
            self.cs_uri_query(),
            self.cs_cookie(),
            self.result_type(),
            self.edge_request_id(),
            self.x_host_header(),
            self.cs_protocol(),
            self.cs_bytes(),
            self.time_taken(),
            self.xforwarded_for(),
            self.ssl_protocol(),
            self.ssl_cipher(),
            self.response_result_type(),
            self.cs_protocol_version(),
            self.fle_status(),
            self.fle_encrypted_fields(),
            self.c_port(),
            self.time_to_first_byte(),
            self.x_edge_detailed_result_type(),
            self.sc_content_type(),
            self.sc_content_len(),
            self.sc_range_start(),
            self.sc_range_end(),
        ]

    def cf_date(self) -> str:
        return f"{self.generator.date_this_decade()}"

    def cf_time(self) -> str:
        return f"{self.generator.time()}"

    def edge_location(self) -> str:
        total_pops = sum(v[1] for v in AWSConstants._cloudfront_edge_locations)
        pop = self.generator.random_element(
            elements=(OrderedDict([(v[0], v[1] / total_pops) for v in AWSConstants._cloudfront_edge_locations]))
        )

        return f"{pop}{self.generator.pyint(50, 58)}-{self.generator.random_element(['C', 'P'])}{self.generator.pyint(1,8)}"  # noqa: E501

    def sc_bytes(self) -> str:
        return self.generator.pyint(min_value=1, max_value=1024 * 1024 * 1024)

    def c_ip(self) -> str:
        return self.generator.random_element([self.generator.ipv4(), self.generator.ipv6()])

    def cs_method(self) -> str:
        return self._http_status_code()

    def cs_host(self) -> str:
        return f"d{self._random_alnum(13)}.cloudfront.net"

    def cs_uri_stem(self) -> str:
        return self.generator.file_path()

    def sc_status(self) -> str:
        return self.generator.random_element(
            elements=OrderedDict(
                [
                    ("000", 0.01),
                    (self._http_status_code(), 0.9),
                ]
            )
        )

    def referer_domain(self) -> str:
        return self.generator.random_element(elements=("-", self.generator.domain_name()))

    def cs_uri_query(self) -> str:
        return self.generator.random_element(
            elements=(
                "-",
                f"{self.generator.word(part_of_speech='verb')}={self.generator.word(part_of_speech='noun')}",
            )
        )

    def cs_cookie(self) -> str:
        return self.cs_uri_query()

    def result_type(self) -> str:
        return self.generator.random_element(
            elements=("Hit", "RefreshHit", "Miss", "LimitExceeded", "CapacityExceeded", "Error", "Redirect")
        )

    def edge_request_id(self) -> str:
        return self._random_alnum(56)

    def x_host_header(self, cs_host: Optional[str] = None) -> str:
        return self.generator.random_element(elements=(self.generator.domain_name(), cs_host or self.cs_host()))

    def cs_protocol(self) -> str:
        return self.generator.random_element(elements=("http", "https", "ws", "wss"))

    def cs_bytes(self) -> int:
        return self.generator.pyint(min_value=1, max_value=1024 * 1024 * 1024)

    def time_taken(self) -> int:
        return self.generator.pyfloat(right_digits=3, positive=True, max_value=1000)

    def xforwarded_for(self) -> str:
        return self.generator.random_element(["-", self.generator.ipv4(), self.generator.ipv6()])

    def ssl_protocol(self, protocol: Optional[str] = None) -> str:
        """
        https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/secure-connections-supported-viewer-protocols-ciphers.html
        """
        if protocol is not None and protocol == "http":
            return "-"

        return self.generator.random_element(elements=("SSLv3", "TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"))

    def ssl_cipher(self, protocol: Optional[str] = None) -> str:
        """
        https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/secure-connections-supported-viewer-protocols-ciphers.html
        """
        if protocol is not None and protocol == "http":
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

    def response_result_type(self) -> str:
        return self.result_type()

    def cs_protocol_version(self) -> str:
        # https://almanac.httparchive.org/en/2020/http
        http_version = self.generator.random_element(
            elements=OrderedDict(
                [
                    ("0.9", 0.01),
                    ("1.0", 0.05),
                    ("1.1", 0.41),
                    ("2.0", 0.38),
                    ("3.0", 0.25),
                ]
            )
        )
        return f"HTTP/{http_version}"

    def fle_status(self, fle_enabled: Optional[bool] = False) -> str:
        if not fle_enabled:
            return "-"

        # TODO: Make the errors line up with status codes
        return self.generator.random_element(
            elements=(
                "ForwardedByContentType",
                "ForwardedByQueryArgs",
                "ForwardedDueToNoProfile",
                "MalformedContentTypeClientError",
                "MalformedInputClientError",
                "MalformedQueryArgsClientError",
                "RejectedByContentType",
                "RejectedByQueryArgs",
                "ServerError",
                "FieldLengthLimitClientError",
                "FieldNumberLimitClientError",
                "RequestLengthLimitClientError",
            )
        )

    def fle_encrypted_fields(self, fle_enabled: Optional[bool] = True) -> str:
        if not fle_enabled:
            return "-"

        return str(self.generator.pyint(1, 10))

    def c_port(self) -> str:
        return str(self.generator.pyint(1000, 65535))

    def time_to_first_byte(self) -> float:
        return self.generator.pyfloat(right_digits=3, positive=True, max_value=1000)

    def x_edge_detailed_result_type(self) -> str:
        # TODO: Handle special cases
        return self.result_type()

    def sc_content_type(self) -> str:
        return self.generator.random_element(
            elements=("text/html", "application/json", "application/xml", "binary/octet-stream")
        )

    def sc_content_len(self) -> str:
        return self.generator.random_element(
            elements=("-", str(self.generator.pyint(min_value=1, max_value=1024 * 1024 * 1024)))
        )

    def sc_range_start(self) -> str:
        return self.generator.random_element(
            elements=("-", str(self.generator.pyint(min_value=1, max_value=1024 * 1024 * 1024)))
        )

    def sc_range_end(self) -> str:
        return self.generator.random_element(
            elements=("-", str(self.generator.pyint(min_value=1, max_value=1024 * 1024 * 1024)))
        )
