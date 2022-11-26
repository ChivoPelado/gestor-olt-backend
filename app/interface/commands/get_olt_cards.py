import os
from ntc_templates.parse import parse_output
from dataclasses import dataclass
from app.interface.task import Task
from app.interface.utils import Payload
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

# Define la carpeta con las plantillas NTC
os.environ["NTC_TEMPLATES_DIR"] = "app/ntc-templates"

@dataclass
class OltGetCards(Task):
    payload: Payload
    description = "Get OLT cards"

    def execute(self):
        device = {
                "device_type": "zte_zxros",
                "host": self.payload.olt_ip_address,
                "port": self.payload.ssh_port,
                "username": self.payload.ssh_user,
                "password": self.payload.ssh_password,
                "conn_timeout": 30,
                "global_delay_factor": 5,
                "session_log": "logging.txt"
            }

        result = self._send_show_command(device, ["show card"])

        return parse_output(platform="zte_zxros", command="show card", data=result.get('show card'))


    def _send_show_command(self, device, commands):
        result = {}
        try:
            with ConnectHandler(**device) as ssh:
                ssh.enable()
                for command in commands:
                    output = ssh.send_command(command)
                    result[command] = output
            return result
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
            print(error)