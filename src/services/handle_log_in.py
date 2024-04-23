from src.db.repositories.user import add_flag, add_tokens, get_flags

TOKENS_TO_GRANT_ON_WELCOME = 3 * 3 * 2


def handle_log_in(user_id: str):
    flags = get_flags(user_id)
    if "welcome_tokens_granted" not in flags:
        # grant welcome points
        add_tokens(user_id, TOKENS_TO_GRANT_ON_WELCOME)
        add_flag(user_id, "welcome_tokens_granted")
