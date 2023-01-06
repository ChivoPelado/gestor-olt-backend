from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
from celery import shared_task


CONN_TIMEOUT = 10
GLOBAL_DELAY_FACTOR = 3
SESSION_LOG_FILE = "logging.txt"

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             name='olt:send_command')
def send_command(self, device: dict, commands = [], expect_string = None):
    result = {}
    device_handler = {
        "host": device.get("host"),
        "port": device.get("port"),
        "username": device.get("username"),
        "password": device.get("password"),
        "device_type": device.get("device_type"),
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