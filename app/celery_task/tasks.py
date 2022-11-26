from celery import shared_task
from app.interface.commands import show_card
from app.interface.controller.olt_controller import OltController
from app.interface.commands.get_onu_signal_level import OnuSignal
from app.interface.commands.get_olt_cards import OltGetCards
from app.interface.utils import Payload

controller = OltController()

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='olt:olt_get_card_task')
def olt_get_card_task(self, payload: Payload):
    olt_cards = controller.get(OltGetCards(payload))
    return olt_cards


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='olt:get_onu_signal_level')
def get_onu_signal_level(self, payload: Payload):

    onu_signal = controller.get(OnuSignal(payload))
    return onu_signal