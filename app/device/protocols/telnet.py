from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
from celery import shared_task
from ntc_templates.parse import parse_output
from typing import Final
import os

os.environ["NTC_TEMPLATES_DIR"] = "templates"

CONN_TIMEOUT = 10
GLOBAL_DELAY_FACTOR = 3
SESSION_LOG_FILE = "logging.txt"

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='olt:send_command')
def send_command(self, device: dict, commands = [], expect_string = None):
    result = {}
    device_handler = {
        **device,
        "conn_timeout": CONN_TIMEOUT,
        "global_delay_factor": GLOBAL_DELAY_FACTOR,
        "session_log": SESSION_LOG_FILE
    }
    try:
        with ConnectHandler(**device_handler) as connection:
            connection.enable()
            for command in commands:
                output = connection.send_command(command, expect_string=expect_string)
                result[command] = output
        return result
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)