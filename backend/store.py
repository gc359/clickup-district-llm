_sessions: dict[str, list[dict]] = {}


def has_session(session_id: str) -> bool:
    return session_id in _sessions


def get_history(session_id: str) -> list[dict]:
    return _sessions.setdefault(session_id, [])


def append_message(session_id: str, message: dict) -> None:
    get_history(session_id).append(message)


def set_history(session_id: str, messages: list[dict]) -> None:
    _sessions[session_id] = messages
