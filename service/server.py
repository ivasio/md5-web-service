import traceback
import pickle
import time

import flask
import pika

from config import SERVER_HOST, SERVER_PORT
from task import Task, InvalidTaskError

app = flask.Flask(__name__)


@app.route('/submit', methods=['POST'])
def submit():
    try:
        url = flask.request.form['url']
    except KeyError:
        return flask.jsonify({'error': 'url must be provided'}), 404
    email = flask.request.form.get('email')

    try:
        task = Task.create_new(url, email)
        payload = pickle.dumps(task.__dict__)

        connection_parameters = Task.get_connection_parameters()
        with pika.BlockingConnection(connection_parameters) as connection:
            channel = connection.channel()
            channel.queue_declare(queue='incoming_tasks', durable=True)
            channel.basic_publish(exchange='', routing_key='incoming_tasks',
                                  body=payload)
    except InvalidTaskError as exc:
        return flask.jsonify({'error': exc.args[0]}), 404
    except Exception:
        traceback.print_exc()
        return flask.jsonify({'error': 'Internal server error'}), 500

    return flask.jsonify({'id': task.id})


@app.route('/check', methods=['GET'])
def check():
    try:
        id = flask.request.args['id']
    except KeyError:
        return flask.jsonify({'error': 'id must be provided'}), 404

    try:
        task_data = Task.get_by_id(id)
    except InvalidTaskError as exc:
        return flask.jsonify({'error': exc.args[0]}), 404
    except Exception:
        traceback.print_exc()
        return flask.jsonify({'error': 'Internal server error'}), 500

    return flask.jsonify(task_data)


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)
