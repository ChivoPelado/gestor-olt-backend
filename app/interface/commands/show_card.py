import os
from ntc_templates.parse import parse_output
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

# Define la carpeta con las plantillas NTC
os.environ["NTC_TEMPLATES_DIR"] = "app/ntc-templates"

def send_show_command(device, commands):
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
        
def get_olt():

    device = {
## DEFINIR PARAMETROS DE CONEXION
    }

    result = send_show_command(device, ["show card"])

    return parse_output(platform="zte_zxros", command="show card", data=result.get('show card'))