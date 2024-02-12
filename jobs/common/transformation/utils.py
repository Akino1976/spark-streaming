import operator
from pyspark.sql.functions import udf
from pyspark.sql.session import SparkSession
from pyspark.sql.types import StringType


@udf(returnType=StringType())
def set_counterparty(column: str) -> str:
    if operator.contains(column, "test"):
        return "core"
 