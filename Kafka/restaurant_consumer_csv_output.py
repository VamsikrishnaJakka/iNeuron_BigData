import argparse
import csv 
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
import pandas as pd


API_KEY = 'PT6IX5GINAO7CXDV'
ENDPOINT_SCHEMA_URL  = 'https://psrc-6zww3.us-east-2.aws.confluent.cloud'
API_SECRET_KEY = 'H0+JfqKhsf1PLSNPST4fL8OCbywyZyy/erDpHq4NvBudzmaQhS+zx7TBbYKhJvyr'
BOOTSTRAP_SERVER = 'pkc-ymrq7.us-east-2.aws.confluent.cloud:9092'
SECURITY_PROTOCOL = 'SASL_SSL'
SSL_MACHENISM = 'PLAIN'
SCHEMA_REGISTRY_API_KEY = 'LBZVP2RUT43SXQOC'
SCHEMA_REGISTRY_API_SECRET = 'jBW4zST3uh3uzDBK9yFrVMrKoTXYSCTMqCklOkRGogHulIhgafyPLjhhNl5tAGFn'


def sasl_conf():

    sasl_conf = {'sasl.mechanism': SSL_MACHENISM,
                 # Set to SASL_SSL to enable TLS support.
                #  'security.protocol': 'SASL_PLAINTEXT'}
                'bootstrap.servers':BOOTSTRAP_SERVER,
                'security.protocol': SECURITY_PROTOCOL,
                'sasl.username': API_KEY,
                'sasl.password': API_SECRET_KEY
                }
    return sasl_conf



def schema_config():
    return {'url':ENDPOINT_SCHEMA_URL,
    
    'basic.auth.user.info':f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}"

    }


class Car:   
    def __init__(self,record:dict):
        for k,v in record.items():
            setattr(self,k,v)
        
        self.record=record
   
    @staticmethod
    def dict_to_car(data:dict,ctx):
        return Car(record=data)

    def __str__(self):
        return f"{self.record}"


def main(topic):
    schema_registry_conf= schema_config()
    schema_registry_client= SchemaRegistryClient(schema_registry_conf)
    schema_str= schema_registry_client.get_latest_version(topic+"-value").schema.schema_str
    json_deserializer = JSONDeserializer(schema_str,from_dict=Car.dict_to_car)

    consumer_conf = sasl_conf()
    consumer_conf.update({
                     'group.id': 'group1',
                     'auto.offset.reset': "earliest"})

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])
    
    records_consumed=0
    columns=['order_number', 'order_date', 'item_name', 'quantity', 'product_price', 'total_products']
    df=pd.DataFrame(columns=['order_number', 'order_date', 'item_name', 'quantity', 'product_price', 'total_products'])
    output_filepath = "C:\\Users\\LENOVO\\Desktop\\output_records.csv"
    df.to_csv(output_filepath, mode='a', index=False)


    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            car = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))

            if Car is not None:
                con_records = car.record
                print(con_records)
                df2 = pd.DataFrame([con_records])
                df2.to_csv(output_filepath, mode='a', index=False, header=False)
                records_consumed=records_consumed+1
                    
            
        except KeyboardInterrupt:
            break
    print("Total records consumed and printed on terminal : ", records_consumed)
    consumer.close()

main("topic_0")