import pika
import json


def send_message(action: str, params: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='request_queue', durable=True, exclusive=True)

    payload = {
        "action": action,
        "params": params
    }

    channel.basic_publish(
        exchange='',
        routing_key='request_queue',
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send dynamic requests to RabbitMQ")
    parser.add_argument("action", type=str, help="The action to trigger (e.g., 'add' or 'delete')")
    parser.add_argument("params", type=str, help="The parameters formatted as a JSON string")

    args = parser.parse_args()

    try:
        parsed_params = json.loads(args.params)
        send_request(action=args.action, params=parsed_params)

    except json.JSONDecodeError as e:
        print(f"[!] Error: The parameters must be a valid JSON string. Details: {e}")
