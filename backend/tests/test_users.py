import pytest
from unittest.mock import AsyncMock, patch

from data_access.cache.keys import build_user_summary_cache_key


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
        "metadata": {
            "cached": False,
            "auth_used": False,
            "rate_limit": {
                "limit": 60,
                "remaining": 58,
                "used": 2,
                "reset": 1779471697,
                "resource": "core",
            },
        },
    }
    with patch(
        "routers.users.users_service.get_user_summary",
        new=AsyncMock(return_value=summary),
    ):
        response = await test_client.get("/users", params={"username": "octocat"})

    assert response.status_code == 200
    assert response.json() == summary


@pytest.mark.asyncio
async def test_rest_repository_uses_cache():
    from data_access.repository.github.rest import GitHubRestUserRepository

    cached_payload = {
        "auth_used": False,
        "data": {
            "username": "octocat",
            "followers_count": 2,
            "repositories": [],
            "metadata": {
                "cached": False,
                "auth_used": False,
                "rate_limit": None,
            },
        },
    }
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=cached_payload)
    cache.set = AsyncMock()
    repository = GitHubRestUserRepository(cache=cache)

    result = await repository.get_user_analysis_source("octocat")

    assert result["username"] == cached_payload["data"]["username"]
    assert result["metadata"]["cached"] is True
    cache.get.assert_awaited_once_with(
        build_user_summary_cache_key("rest", "octocat", False)
    )
    cache.set.assert_not_called()
