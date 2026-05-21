import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_users_rest_summary_endpoint(test_client):
    summary = {
        "username": "octocat",
        "followers_count": 2,
        "repositories": [
            {
                "name": "hello-world",
                "url": "https://github.com/octocat/hello-world",
                "primary_language": "Python",
                "technologies": ["Python", "Docker"],
            }
        ],
        "most_used_language": "Python",
        "technologies": ["Docker", "Python"],
        "messages": [],
    }
    with patch(
        "routers.users.users_service.get_user_summary",
        new=AsyncMock(return_value=summary),
    ):
        response = await test_client.get("/users", params={"username": "octocat"})

    assert response.status_code == 200
    assert response.json() == summary
