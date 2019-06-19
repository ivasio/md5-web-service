import os
import smtplib
import config
import ssl

import traceback


def send_email(hash_sum: str, task_id: str, email: str) -> None:
    if hash_sum:
        message = "MD5 hash of task {} : {}".format(task_id, hash_sum)
    else:
        message = "Task {} finished with error".format(task_id)

    body = "\n".join((
        "From: %s" % config.SMTP_EMAIL,
        "To: %s" % email,
        "Subject: MD5 calculation result",
        "",
        message
    ))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT,
                              context=context) as server:
                server.login(config.SMTP_EMAIL, config.SMTP_PASSWORD)
                server.sendmail(config.SMTP_EMAIL, email, body)
    except Exception:
        traceback.print_exc()
