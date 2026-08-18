from config import Settings


def test_ollama_host_gets_http_scheme_when_missing():
    settings = Settings(ollama_host="localhost:11434")
    assert settings.ollama_host == "http://localhost:11434"


def test_ollama_host_with_scheme_is_unchanged():
    settings = Settings(ollama_host="https://ollama.internal:11434")
    assert settings.ollama_host == "https://ollama.internal:11434"


def test_clickup_ticket_list_name_default():
    settings = Settings()
    assert settings.clickup_ticket_list_name == "Support Tickets"


def test_clickup_ticket_list_name_override():
    settings = Settings(clickup_ticket_list_name="District Helpdesk")
    assert settings.clickup_ticket_list_name == "District Helpdesk"


def test_clickup_kb_folder_name_default():
    settings = Settings()
    assert settings.clickup_kb_folder_name == "Knowledge Base"


def test_clickup_kb_folder_name_override():
    settings = Settings(clickup_kb_folder_name="IT Docs")
    assert settings.clickup_kb_folder_name == "IT Docs"
