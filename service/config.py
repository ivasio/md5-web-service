SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

RABBITMQ_HOST = 'queue'
RABBITMQ_PORT = 5672

SMTP_HOST = 'smtp.yandex.ru'
SMTP_PORT = 465
SMTP_EMAIL = 'dgfchbjnm@yandex.ru'
SMTP_PASSWORD = 'dgfchbjnmpass'

DB_USER = 'postgres'
DB_PASSWORD = 'pass'
DB_HOST = 'db'
DB_PORT = 5432
DB_STRING = 'postgres://{}:{}@{}:{}'.format(DB_USER, DB_PASSWORD,
                                            DB_HOST, DB_PORT)

DOWNLOAD_DIR = 'files/'
