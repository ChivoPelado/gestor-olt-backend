
from app.apis.v1.agent.crud import create_agent
from app.apis.v1.auth.crud import get_agent
from fastapi.testclient import TestClient
from app.core.schemas.agent import AgentCreate
from sqlalchemy.orm import Session


#Define las cabeceras con el token para el acceso a puntos restringidos
def user_authentication_headers(client: TestClient, email: str, password: str):
    data = {"username": email, "password": password}
    r = client.post("/api/v1/auth/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {
        "Authorization": f"Bearer {auth_token}",
        'Content-Type': 'application/json'}
    return headers



def authentication_token_from_email(client_test: TestClient, email: str, db: Session):
    """
    Retorna un token valido si usuario existe,
    caso contrario lo crea
    """
    password = "random-passW0rd"
    user = get_agent(username=email, db=db)
    if not user:
        user_in_create = AgentCreate(
            name="Test Agent", 
            email=email, 
            hashed_password=password,            
            is_active=True,
            role='Administrador',
            scopes=[]
    )
        user = create_agent(db=db, agent=user_in_create)
    return user_authentication_headers(client=client_test, email=email, password=password)
