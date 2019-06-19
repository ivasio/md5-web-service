import os
import subprocess
import hashlib
import re
import traceback

import pika

import config
import model
import emailing


class InvalidTaskError(ValueError):
    pass


class TaskFailedError(RuntimeError):
    pass


class Task(object):

    def __init__(self, url: str, email: str, id: int = -1):
        self.id = id
        self.validate_url(url)
        self.url = url
        if email:
            self.validate_email(email)
            self.email = email
        else:
            self.email = ''

    @classmethod
    def create_new(cls, url: str, email: str = ''):
        task = cls(url, email)
        task.id = model.create_new_task(url)
        return task

    @classmethod
    def get_by_id(cls, task_id: str):
        db_task = model.get_by_id(task_id)
        if not db_task:
            raise InvalidTaskError(
                'task with id {} was not found'.format(task_id))

        result = {'status': db_task.status}
        if db_task.status == model.Task.SUCCESS:
            result['id'] = db_task.id
            result['url'] = db_task.url
            result['md5'] = db_task.md5
        elif db_task.status == model.Task.ERROR:
            raise TaskFailedError()

        return result

    def process_task(self) -> None:
        self.file_path = os.path.join(
            config.DOWNLOAD_DIR, 'hgjbkn', str(self.id))
        try:
            self.download_file()
            hash_sum = self.get_hash()
        except Exception:
            hash_sum = ''
            traceback.print_exc()

        self.delete_file()

        model.write_result(self.id, hash_sum)
        if self.email:
            emailing.send_email(hash_sum, self.id, self.email)

    def download_file(self) -> None:
        try:
            subprocess.run(['wget', '-O', self.file_path, self.url],
                           capture_output=True, check=True)
        except subprocess.CalledProcessError:
            raise TaskFailedError()

    def get_hash(self) -> None:
        result = hashlib.md5()
        with open(self.file_path, 'rb') as file:
            while True:
                chunk = file.read(128)
                if not chunk:
                    break
                result.update(chunk)
        return result.hexdigest()

    def delete_file(self) -> None:
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            pass

    @staticmethod
    def get_connection_parameters():
        return pika.ConnectionParameters(
            host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT,
            retry_delay=2, connection_attempts=10)

    def validate_url(self, url: str):
        if not re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+$', url):
            raise InvalidTaskError('invalid url')

    def validate_email(self, email: str):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                        email):
            raise InvalidTaskError('invalid email')
