import pika
import json
from pydantic import BaseModel, ValidationError
from typing import Any, Optional, TypedDict


class QueueRequest(BaseModel):
    action: str
    params: dict = {}

class AddUserParams(TypedDict):
    username: str
    age: int

class QueueResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None

def add_user(params: AddUserParams):
    return f"Added {params['username']}, age {params['age']}"

ACTION_ROUTER = {
    "add": {"schema": AddUserParams, "handler": add_user},
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

        response = QueueResponse(status="success", data=result)

    except ValidationError as error:
        response = QueueResponse(status="Error", data=error)
    except Exception as error:
        response = QueueResponse(status="Error", data=error)

    ch.basic_publish(exchange='', routing_key='response_queue', body=response.model_dump_json())

    print(f"[*] Sent response: {response.model_dump_json()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='response_queue', durable=True, exclusive=True)
    channel.queue_declare(queue='request_queue', durable=True, exclusive=True)
    channel.basic_consume(queue='request_queue', on_message_callback=on_message_received)

    channel.start_consuming()

if __name__ == "__main__":
    main()