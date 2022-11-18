from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.apis.v1.auth import crud
from fastapi_login.exceptions import InvalidCredentialsException
from app.core.utils.security import verify_password, login_manager
from app.core.schemas.token import Token

router = APIRouter()

@router.post('/auth/login', response_model=Token)
def login(db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()) -> Token:
    email = data.username
    password = data.password

    print(email)
    print(password)

    user = crud.get_agent(username=email, db=db)
    if not user:
        print("invalid 1")
        # you can return any response or error of your choice
        raise InvalidCredentialsException
    
    if not verify_password(password, user.hashed_password):
        print("invalid 2")
        raise InvalidCredentialsException

    token = login_manager.create_access_token(data={'sub': user.email})
    return Token(access_token=token, token_type='bearer')