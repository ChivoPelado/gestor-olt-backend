from celery import group
from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.interface.commands import show_card

router = APIRouter()


@router.get("/sys/olt/get_card/")
def get_olt_card() -> dict:
    """
    Retorna información de las tarjetas de OLT
    """
    data: dict = {}
    data =  show_card.get_olt()
    return data