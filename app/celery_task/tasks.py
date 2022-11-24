from celery import shared_task
from app.interface.commands import show_card
from app.interface.controller.olt_controller import OltController
from app.interface.commands.get_onu_signal_level import OnuSignal
from app.interface.utils import Payload

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='olt:olt_show_card_task')
def olt_show_card_task():
    result = show_card.get_olt()
    return result


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='olt:get_onu_signal_level')
def get_onu_signal_level(self, payload: Payload):
    controller = OltController()
    onu_signal = controller.get(OnuSignal(payload))
    return onu_signal