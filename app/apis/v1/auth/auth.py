from fastapi import Depends, APIRouter, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.apis.v1.auth import crud
from fastapi_login.exceptions import InvalidCredentialsException
from app.core.utils.security import Hasher, login_manager
from app.core.schemas.generic import IResponseBase
from app.core.schemas.token import Token
from app.core.schemas.agent import AgentResponse
from app.core.models.log import LoginLog

router = APIRouter()

@router.post('/login', response_model=Token)
def login(req: Request, db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()) -> Token:
    email = data.username
    password = data.password

    action: str = None
    agent_id: int = None
    ip_address = req.client.host

    #login_log: LoginLog = LoginLog()

    agent_id = crud.get_agent_id_by_email(email, db)

    #print(agent_id[0])

    user = crud.get_agent(username=email, db=db)
    if not user:
        # Ajustar respuesta
        raise InvalidCredentialsException

    """         try:
            print(agent_id)
            #agent_id = agent_id[0]

        except Exception:
            raise InvalidCredentialsException """

    
    if not Hasher.verify_password(password, user.hashed_password):

        db.add(LoginLog(agent_id= agent_id[0], action="Proceso de autenticación fallido", ip_address=ip_address))
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales proporcionadas inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        ) 
        #InvalidCredentialsException
    print(agent_id[0])

   
    db.add(LoginLog(agent_id= agent_id[0], action="Autenticado correctamente", ip_address=ip_address))
    db.commit()

    token = login_manager.create_access_token(data={'sub': user.email})
    return Token(access_token=token, token_type='bearer')


@router.get('/me', response_model=IResponseBase[AgentResponse])
def get_logedin_agent(db: Session = Depends(get_db), agent: AgentResponse = Depends(login_manager)) -> IResponseBase[AgentResponse]:
    return IResponseBase[AgentResponse](response=agent)