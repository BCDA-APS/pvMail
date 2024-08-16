from ..ini_config import Config


def test_Config():
    con = Config()
    assert con is not None
    assert isinstance(con.ini_file, str)
    assert len(con.agent_db) > 0
