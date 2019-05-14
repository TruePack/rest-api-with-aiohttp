async def test_registration(client):
    credentials = {"username": "test_user", "password": "test_password"}
    post_resp = await client.post(
        '/api/v1/users/registration/',
        json=credentials)

    assert post_resp.status == 201


async def test_login(client):
    credentials = {"username": "test_user", "password": "test_password"}
    post_resp = await client.post(
        '/api/v1/users/login/',
        json=credentials)

    assert 'token' in await post_resp.json()

    assert post_resp.status == 200


async def test_generate_joke_without_token(client):
    post_resp = await client.post(
        '/api/v1/jokes/')

    assert post_resp.status == 401


async def test_generate_joke(client):
    credentials = {"username": "test_user", "password": "test_password"}
    auth_response = await client.post('/api/v1/users/login/', json=credentials)
    response_with_token = await auth_response.json()
    token = response_with_token["token"]

    post_resp = await client.post(
        '/api/v1/jokes/', headers={"authorization": token})

    assert post_resp.status == 201


async def test_list_of_joke(client):
    credentials = {"username": "test_user", "password": "test_password"}
    auth_response = await client.post('/api/v1/users/login/', json=credentials)
    response_with_token = await auth_response.json()
    token = response_with_token["token"]

    get_resp = await client.get(
        "/api/v1/jokes/", headers={"authorization": token})

    assert get_resp.status == 200


async def test_update_joke(client):
    credentials = {"username": "test_user", "password": "test_password"}
    auth_response = await client.post('/api/v1/users/login/', json=credentials)
    response_with_token = await auth_response.json()
    token = response_with_token["token"]

    patch_resp = await client.patch(
        '/api/v1/jokes/1/',
        headers={"authorization": token},
        json={"text": "__new joke's text__"})

    assert patch_resp.status == 200


async def test_joke(client):
    credentials = {"username": "test_user", "password": "test_password"}
    auth_response = await client.post('/api/v1/users/login/', json=credentials)
    response_with_token = await auth_response.json()
    token = response_with_token["token"]

    get_resp = await client.get(
        '/api/v1/jokes/1/',
        headers={"authorization": token})
    assert get_resp.status == 200


async def test_delete_joke(client):
    credentials = {"username": "test_user", "password": "test_password"}
    auth_response = await client.post('/api/v1/users/login/', json=credentials)
    response_with_token = await auth_response.json()
    token = response_with_token["token"]

    del_resp = await client.delete(
        '/api/v1/jokes/1/',
        headers={"authorization": token})

    assert del_resp.status == 204
