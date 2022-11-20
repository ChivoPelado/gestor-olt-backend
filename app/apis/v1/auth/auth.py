from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.apis.v1.auth import crud
from fastapi_login.exceptions import InvalidCredentialsException
from app.core.utils.security import Hasher, login_manager
from app.core.schemas.generic import IResponseBase
from app.core.schemas.token import Token
from app.core.schemas.agent import AgentResponse

router = APIRouter()

@router.post('/auth/login', response_model=Token)
def login(db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()) -> Token:
    email = data.username
    password = data.password

    user = crud.get_agent(username=email, db=db)
    if not user:
        # Ajustar respuesta
        raise InvalidCredentialsException
    
    if not Hasher.verify_password(password, user.hashed_password):
        raise InvalidCredentialsException

    token = login_manager.create_access_token(data={'sub': user.email})
    return Token(access_token=token, token_type='bearer')


@router.post('/auth/me', response_model=IResponseBase[AgentResponse])
def get_logedin_agent(db: Session = Depends(get_db), agent: AgentResponse = Depends(login_manager)) -> IResponseBase[AgentResponse]:
    return IResponseBase[AgentResponse](response=agent)