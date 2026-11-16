import os

os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-12345"
os.environ["ENVIRONMENT"] = "testing"

import time
from unittest.mock import AsyncMock, patch
import jwt as pyjwt
import pytest
from httpx import ASGITransport, AsyncClient

from main import JWT_SECRET, app


def make_token(user_id="user_12345", expired=False, secret=None):
    payload = {"user_id": user_id}
    if expired:
        payload["exp"] = int(time.time()) - 3600
    else:
        payload["exp"] = int(time.time()) + 3600
    return pyjwt.encode(payload, secret or JWT_SECRET, algorithm="HS256")


def get_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def valid_token():
    return make_token()


@pytest.fixture
def expired_token():
    return make_token(expired=True)


@pytest.fixture
def auth_headers(valid_token):
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture(autouse=True)
def mock_chat():
    """Dynamically mock main.chat without polluting sys.modules"""
    with patch("main.chat", new_callable=AsyncMock) as mock:
        mock.return_value = "Welcome! How can I help you today?"
        yield mock


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    try:
        if hasattr(app.state.limiter, "reset"):
            app.state.limiter.reset()
        elif hasattr(app.state.limiter, "_limiter") and hasattr(app.state.limiter._limiter, "storage"):
            app.state.limiter._limiter.storage.clear()
    except Exception:
        pass
    yield


class TestMockTokenEndpoint:

    @pytest.mark.unit
    async def test_returns_200(self):
        async with get_client() as client:
            response = await client.get("/api/v1/auth/mock-token")
            assert response.status_code == 200

    @pytest.mark.unit
    async def test_returns_valid_jwt(self):
        async with get_client() as client:
            response = await client.get("/api/v1/auth/mock-token")
            data = response.json()
            assert "access_token" in data
            payload = pyjwt.decode(
                data["access_token"], JWT_SECRET, algorithms=["HS256"]
            )
            assert payload["user_id"] == "user_12345"

    @pytest.mark.unit
    async def test_token_can_be_used_for_chat(self):
        async with get_client() as client:
            token_resp = await client.get("/api/v1/auth/mock-token")
            token = token_resp.json()["access_token"]
            chat_resp = await client.post(
                "/api/v1/chat",
                json={"message": "Hello"},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert chat_resp.status_code == 200


class TestChatAuthentication:

    @pytest.mark.unit
    async def test_valid_token_returns_200(self, auth_headers):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Hi"},
                headers=auth_headers
            )
            assert response.status_code == 200

    @pytest.mark.unit
    async def test_no_token_returns_401(self):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Hi"}
            )
            assert response.status_code == 401

    @pytest.mark.unit
    async def test_invalid_token_returns_401(self):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Hi"},
                headers={"Authorization": "Bearer totally.fake.token"}
            )
            assert response.status_code == 401

    @pytest.mark.unit
    async def test_expired_token_returns_401(self, expired_token):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Hi"},
                headers={"Authorization": f"Bearer {expired_token}"}
            )
            assert response.status_code == 401

    @pytest.mark.unit
    async def test_wrong_secret_returns_401(self):
        hacker_token = make_token(user_id="hacker", secret="wrong-secret-for-testing-only-123456789")
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Hi"},
                headers={"Authorization": f"Bearer {hacker_token}"}
            )
            assert response.status_code == 401


class TestChatFunctionality:

    @pytest.mark.unit
    async def test_returns_agent_reply(self, auth_headers, mock_chat):
        mock_chat.return_value = "Your order has been shipped!"
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Where is my order?", "session_id": "s1"},
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.json()["reply"] == "Your order has been shipped!"

    @pytest.mark.unit
    async def test_thread_id_is_user_plus_session(self, auth_headers, mock_chat):
        async with get_client() as client:
            await client.post(
                "/api/v1/chat",
                json={"message": "Hi", "session_id": "sess_abc"},
                headers=auth_headers
            )
            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args.kwargs
            assert call_kwargs["thread_id"] == "user_12345_sess_abc"
            assert call_kwargs["user_input"] == "Hi"

    @pytest.mark.unit
    async def test_default_session_id(self, auth_headers, mock_chat):
        async with get_client() as client:
            await client.post(
                "/api/v1/chat",
                json={"message": "Hi"},
                headers=auth_headers
            )
            call_kwargs = mock_chat.call_args.kwargs
            assert call_kwargs["thread_id"] == "user_12345_default"

    @pytest.mark.unit
    async def test_different_users_get_different_threads(self, mock_chat):
        token_a = make_token(user_id="user_A")
        token_b = make_token(user_id="user_B")
        async with get_client() as client:
            await client.post(
                "/api/v1/chat",
                json={"message": "Hi", "session_id": "shared"},
                headers={"Authorization": f"Bearer {token_a}"}
            )
            thread_a = mock_chat.call_args.kwargs["thread_id"]
            await client.post(
                "/api/v1/chat",
                json={"message": "Hi", "session_id": "shared"},
                headers={"Authorization": f"Bearer {token_b}"}
            )
            thread_b = mock_chat.call_args.kwargs["thread_id"]
            assert thread_a != thread_b
            assert thread_a == "user_A_shared"
            assert thread_b == "user_B_shared"


class TestChatErrorHandling:

    @pytest.mark.unit
    async def test_agent_crash_returns_500(self, auth_headers, mock_chat):
        mock_chat.side_effect = Exception("Gemini API is down")
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"message": "Hello"},
                headers=auth_headers
            )
            assert response.status_code == 500
            assert "Gemini API is down" in response.json()["detail"]


class TestChatValidation:

    @pytest.mark.unit
    async def test_missing_message_returns_422(self, auth_headers):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={"session_id": "s1"},
                headers=auth_headers
            )
            assert response.status_code == 422

    @pytest.mark.unit
    async def test_empty_json_returns_422(self, auth_headers):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                json={},
                headers=auth_headers
            )
            assert response.status_code == 422

    @pytest.mark.unit
    async def test_invalid_json_body_returns_422(self, auth_headers):
        async with get_client() as client:
            response = await client.post(
                "/api/v1/chat",
                content="this is not json",
                headers={**auth_headers, "Content-Type": "application/json"}
            )
            assert response.status_code == 422


class TestRateLimiting:

    @pytest.mark.integration
    async def test_exceeding_rate_limit_returns_429(self, auth_headers):
        async with get_client() as client:
            for i in range(10):
                resp = await client.post(
                    "/api/v1/chat",
                    json={"message": f"msg {i}"},
                    headers=auth_headers
                )
                assert resp.status_code == 200
            resp = await client.post(
                "/api/v1/chat",
                json={"message": "one too many"},
                headers=auth_headers
            )
            assert resp.status_code == 429