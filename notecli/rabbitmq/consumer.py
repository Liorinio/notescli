import functools
import logging
import os
import time
import pika
import json
from pika.exceptions import AMQPConnectionError
from pydantic import ValidationError
from notecli.app_types.rabbitmq_validation_models import AddNoteParams, QueueResponse, QueueRequest, DeleteNoteParams, UpdateNoteParams, GetAllNotesParams, ViewNoteParams, MetadatNoteParams, NavigateNoteParams, SearchNoteParams
from notecli.database.database_manager import PostgresDb
from notecli.exceptions.not_found_exception import NotFoundError
from notecli.memory_storage.db_schema import MemoryStorage
from notecli.rabbitmq.rabbitmq_logic_connectors import add_connector, delete_connector, get_all_notes_connector, metadata_connector,navigate_connector, search_connector,update_connector,view_connector
from dotenv import load_dotenv

load_dotenv()

ACTION_ROUTER = {
    "add": {"schema": AddNoteParams, "handler": add_connector},
    "delete": {"schema": DeleteNoteParams, "handler": delete_connector},
    "update" :{"schema": UpdateNoteParams, "handler" :update_connector},
    "list" :{"schema": GetAllNotesParams, "handler" : get_all_notes_connector},
    "view" : {"schema": ViewNoteParams, "handler" :view_connector},
    "metadata" : {"schema": MetadatNoteParams , "handler" :metadata_connector},
    "navigate" : {"schema": NavigateNoteParams , "handler" :navigate_connector},
    "search" : {"schema": SearchNoteParams, "handler" :search_connector}
    }


logger = logging.getLogger(__name__)

def on_message_received(ch, method, properties, body, db):
    try:
        raw_payload = json.loads(body)
        request = QueueRequest(**raw_payload)

        if request.action not in ACTION_ROUTER:
            raise ValueError(f"Unknown action: {request.action}")

        route = ACTION_ROUTER[request.action]
        validated_params = route["schema"](**request.params)
        result = route["handler"](validated_params, db)

        message_status = "success"
        if result is None or "error" in result:
            message_status = "error"

        response = QueueResponse(status=message_status, data=result)

    except ValidationError as error:
        response = QueueResponse(status="Validation Error", data=str(error.errors()))
    except NotFoundError as error:
        response = QueueResponse(status="Not Found Error", data=str(error))
    except Exception as error:
        response = QueueResponse(status="Error", data=str(error))

    ch.basic_publish(exchange='', routing_key='response_queue', body=response.model_dump_json())
    logger.info(f"Sent response: {response.model_dump_json()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def cons_main():
    db = MemoryStorage()
    db = db.parse_from_dict(PostgresDb.load_from_db())
    logger.info("The database has been loaded, layer: rabbitmq")

    connection = None

    try:
        mq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        mq_port = int(os.getenv("RABBITMQ_PORT", 5672))
        mq_user = os.getenv("RABBITMQ_USER", "guest")
        mq_pass = os.getenv("RABBITMQ_PASSWORD", "guest")

        credentials = pika.PlainCredentials(mq_user, mq_pass)
        connection_params = pika.ConnectionParameters(
            host=mq_host,
            port=mq_port,
            credentials=credentials
        )

        connection = None
        max_retries = 5

        for attempt in range(max_retries):
            try:
                print(f"[*] Attempting to connect to RabbitMQ (Attempt {attempt + 1}/{max_retries})...")
                connection = pika.BlockingConnection(connection_params)
                print("[*] Successfully connected to RabbitMQ!")
                break
            except pika.exceptions.AMQPConnectionError:
                print("[!] RabbitMQ is not ready yet. Waiting 5 seconds...")
                time.sleep(5)

        if not connection:
            raise Exception("Failed to connect to RabbitMQ after maximum retries. Exiting.")

        channel = connection.channel()
        channel.queue_declare(queue='response_queue', durable=True)
        channel.queue_declare(queue='request_queue', durable=True)

        def callback_wrapper(ch, method, properties, body):
            on_message_received(ch, method, properties, body, db)

        channel.basic_consume(
            queue='request_queue',
            on_message_callback=callback_wrapper,
            auto_ack=False
        )

        print("[*] Worker is waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Stopping worker...")

    finally:
        db = None
        logger.info("The database is shutting down, layer: rabbitmq")

        if connection is not None and 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("RabbitMQ connection closed.")


if __name__ == "__main__":
    cons_main()