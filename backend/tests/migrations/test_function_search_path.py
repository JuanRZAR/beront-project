from sqlalchemy import text


def test_functions_pin_search_path_and_deny_public_execution(database):
    with database[2].begin() as connection:
        functions = (
            "FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = 'beront_api'"
        )
        total = connection.scalar(text("SELECT count(*) " + functions))
        assert total >= 93
        pinned = connection.scalar(
            text(
                "SELECT count(*) " + functions + " AND p.prosecdef AND p.proconfig = "
                "ARRAY['search_path=pg_catalog, public, beront_api, pg_temp']"
            )
        )
        assert pinned == total
        assert not connection.scalar(
            text(
                "SELECT bool_or(a.grantee = 0) FROM pg_proc p "
                "JOIN pg_namespace n ON n.oid = p.pronamespace, aclexplode(p.proacl) a "
                "WHERE n.nspname = 'beront_api'"
            )
        )
        assert not connection.scalar(
            text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")
        )
