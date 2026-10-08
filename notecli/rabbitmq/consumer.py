import pika
import json
from pydantic import BaseModel, ValidationError
from typing import Any, Optional, TypedDict
from notecli.app_types.rabbitmq_validation_models import NavigateNoteParams, AddNoteParams, DeleteNoteParams, GetAllNotesParams, SearchNoteParams, ViewNoteParams, QueueResponse, UpdateNoteParams


ACTION_ROUTER = {
    "addUser": {"schema": AddUserParams, "handler": add_user},
    "add": {"schema": AddNoteParams, "handler": add_handler}
    #todo - create a flie of rabbitmq-handlers which use the note handlers that the restapi uses
}

def add_user(params: AddUserParams):
    return f"Added {params['username']}, age {params['age']}"

def on_message_received(ch, method, properties, body):
    try:
        raw_payload = json.loads(body)
        request = QueueRequest(**raw_payload)

        if request.action not in ACTION_ROUTER:
            raise ValueError(f"Unknown action: {request.action}")

        route = ACTION_ROUTER[request.action]
        validated_params = route["schema"](**request.params)
        result = route["handler"](validated_params)

        response = QueueResponse(status="success", data=result)

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