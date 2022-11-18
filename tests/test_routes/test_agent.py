

def test_agent_create(client_test):

    data = {
        "name": "string",
        "email": "user@example.com",
        "hashed_password": "string",
        "is_active": True,
        "role": "Administrador",
        "scopes": []
    }
    response = client_test.post('/api/v1/agent/', json=data)
    assert response.status_code == 200
    

# Prueba la lectura de un agente
def test_get_agent_by_id(client_test):
    response = client_test.get('/api/v1/agent/1')
    assert response.status_code == 200
    assert response.json()["status"] == True


# Prueba de respuesta a agente no encontrado
def test_agent_id_not_found(client_test):
    response = client_test.get('/api/v1/agent/2')
    assert response.status_code == 404
    assert response.json()["detail"] == "Agente no encontrado"


# Prueba de intento de creación de usuario con email existente
def test_agent_create_email_exists(client_test):
    data = {
        "name": "string",
        "email": "user@example.com",
        "hashed_password": "string",
        "is_active": True,
        "role": "Administrador",
        "scopes": []
    }
    response = client_test.post('/api/v1/agent/', json=data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Agente existe"     


# Prueba de eliminación de Agente
def test_agent_delete(client_test):
    response = client_test.delete('/api/v1/agent/1')
    assert response.status_code == 200
    assert response.json()["status"] == True

