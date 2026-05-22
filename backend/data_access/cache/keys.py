def build_user_summary_cache_key(
    upstream: str,
    username: str,
    auth_used: bool,
) -> str:
    auth_mode = "auth" if auth_used else "anon"
    return f"github:{upstream}:user-summary:{auth_mode}:{username.lower()}"
