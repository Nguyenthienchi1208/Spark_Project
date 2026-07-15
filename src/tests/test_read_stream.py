import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark_session():
    return SparkSession.builder \
        .master("local[*]") \
        .appName("Glamira-Raw-Cast-Validation") \
        .getOrCreate()


def test_transform_stream_should_cast_schema_correctly(spark_session):
    mock_kafka_data = [
        (b"key_1", b"""{
            "_id": "5ed8cb0b5139e436c44c0b47",
            "local_time": "2020-06-04 12:20:15",
            "collection": "add_to_cart_action",
            "product_id": "89592",
            "price": "1 278,00",
            "option": [
                {
                    "option_label": "alloy",
                    "option_id": "105683",
                    "value_label": "Yellow Gold 750",
                    "value_id": "765253"
                }
            ]
        }"""),
        (b"key_2", b"""{
            "_id": "5ed8c9bee0da54376c3933cf",
            "local_time": "2020-06-04 12:15:24",
            "collection": "checkout",
            "email_address": "pereira.vivien@yahoo.fr",
            "cart_products": [
                {
                    "product_id": "110474",
                    "amount": "1"
                }
            ]
        }""")
    ]

    raw_df = spark_session.createDataFrame(mock_kafka_data, ["key", "value"])

    from read_stream import transform_stream
    casted_df = transform_stream(raw_df)

    records = {row["event_id"]: row for row in casted_df.collect()}

    assert len(records) == 2

    cart_event = records.get("5ed8cb0b5139e436c44c0b47")
    assert cart_event is not None
    assert cart_event["collection"] == "add_to_cart_action"
    assert cart_event["price"] == "1 278,00"
    assert len(cart_event["option"]) == 1
    assert cart_event["option"][0]["option_label"] == "alloy"
    assert cart_event["option"][0]["value_id"] == "765253"
    assert cart_event["option"][0]["value_label"] == "Yellow Gold 750"

    checkout_event = records.get("5ed8c9bee0da54376c3933cf")
    assert checkout_event is not None
    assert checkout_event["email_address"] == "pereira.vivien@yahoo.fr"
    assert len(checkout_event["cart_products"]) == 1
    assert checkout_event["cart_products"][0]["product_id"] == "110474"
    assert checkout_event["cart_products"][0]["amount"] == "1"
