from app.worker import process_order, mark_failed


class FakeDB:
    def __init__(self):
        self.calls = []

    def execute(self, stmt, params=None):
        sql = str(stmt)
        self.calls.append((sql, params or {}))


def test_process_order_sets_processing_then_processed():
    db = FakeDB()
    process_order(db, order_id=123)

    assert len(db.calls) == 2

    sql1, params1 = db.calls[0]
    sql2, params2 = db.calls[1]

    assert "UPDATE orders" in sql1
    assert "status='PROCESSING'" in sql1
    assert params1["id"] == 123

    assert "UPDATE orders" in sql2
    assert "status='PROCESSED'" in sql2
    assert params2["id"] == 123


def test_mark_failed_truncates_error_to_500_chars():
    db = FakeDB()
    long_error = "x" * 1000

    mark_failed(db, order_id=55, error=long_error)

    assert len(db.calls) == 1
    sql, params = db.calls[0]
    assert "status='FAILED'" in sql
    assert params["id"] == 55
    assert "err" in params
    assert len(params["err"]) == 500
