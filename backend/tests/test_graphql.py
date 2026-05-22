import pytest
from unittest.mock import AsyncMock, patch

from data_access.cache.keys import build_user_summary_cache_key


@pytest.mark.asyncio
async def test_graphql_health_query(test_client):
    response = await test_client.post(
        "/graphql",
        json={"query": "query { health }"},
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"health": "ok"}}


@pytest.mark.asyncio
async def test_graphql_get_is_not_allowed(test_client):
    response = await test_client.get("/graphql")

    assert response.status_code == 405


@pytest.mark.asyncio
async def test_graphql_user_summary_query(test_client):
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
        "models.graphql.GitHubUsers.get_user_summary",
        new=AsyncMock(return_value=summary),
    ):
        response = await test_client.post(
            "/graphql",
            json={
                "query": "query($username: String!) { userSummary(username: $username) { username followersCount mostUsedLanguage technologies messages repositories { name url primaryLanguage technologies } } }",
                "variables": {"username": "octocat"},
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "userSummary": {
                "username": "octocat",
                "followersCount": 2,
                "mostUsedLanguage": "Python",
                "technologies": ["Docker", "Python"],
                "messages": [],
                "repositories": [
                    {
                        "name": "hello-world",
                        "url": "https://github.com/octocat/hello-world",
                        "primaryLanguage": "Python",
                        "technologies": ["Python", "Docker"],
                    }
                ],
            }
        }
    }


@pytest.mark.asyncio
async def test_graphql_user_summary_error_returns_graphql_errors(test_client):
    with patch(
        "models.graphql.GitHubUsers.get_user_summary",
        new=AsyncMock(side_effect=Exception("boom")),
    ):
        response = await test_client.post(
            "/graphql",
            json={
                "query": "query($username: String!) { userSummary(username: $username) { username } }",
                "variables": {"username": "octocat"},
            },
        )

    assert response.status_code == 200
    assert response.json()["data"] is None
    assert response.json()["errors"] == [{"message": "boom"}]


@pytest.mark.asyncio
async def test_graphql_repository_uses_cache():
    from data_access.repository.github.graphql import GitHubGraphQLUserRepository

    cached_payload = {
        "auth_used": True,
        "data": {
            "username": "octocat",
            "followers_count": 2,
            "repositories": [],
        },
    }
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=cached_payload)
    cache.set = AsyncMock()
    repository = GitHubGraphQLUserRepository(cache=cache)

    result = await repository.get_user_analysis_source("octocat", token="token")

    assert result == cached_payload["data"]
    cache.get.assert_awaited_once_with(
        build_user_summary_cache_key("graphql", "octocat", True)
    )
    cache.set.assert_not_called()
