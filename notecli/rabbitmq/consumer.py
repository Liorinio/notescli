import pika
import json
from pydantic import ValidationError
from notecli.app_types.rabbitmq_validation_models import AddNoteParams, QueueResponse, QueueRequest, DeleteNoteParams, \
    UpdateNoteParams, GetAllNotesParams, ViewNoteParams, MetadatNoteParams, NavigateNoteParams, SearchNoteParams
from notecli.rabbitmq.rabbitmq_logic_connectors import add_connector, delete_connector, get_all_notes_connector, metadata_connector,navigate_connector, search_connector,update_connector,view_connector

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


def on_message_received(ch, method, properties, body):
    try:
        raw_payload = json.loads(body)
        request = QueueRequest(**raw_payload)

        if request.action not in ACTION_ROUTER:
            raise ValueError(f"Unknown action: {request.action}")

        route = ACTION_ROUTER[request.action]
        validated_params = route["schema"](**request.params)
        result = route["handler"](validated_params)

        message_status = "success"
        if result is None:
            message_status = "error"

        response = QueueResponse(status=message_status, data=result)

    except ValidationError as error:
        response = QueueResponse(status="Error", data=error)
    except Exception as error:
        response = QueueResponse(status="Error", data=error)

    ch.basic_publish(exchange='', routing_key='response_queue', body=response.model_dump_json())

    print(f"[*] Sent response: {response.model_dump_json()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def cons_main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='response_queue', durable=True)
    channel.queue_declare(queue='request_queue', durable=True)
    channel.basic_consume(queue='request_queue', on_message_callback=on_message_received)

    channel.start_consuming()


if __name__ == "__main__":
    cons_main()
