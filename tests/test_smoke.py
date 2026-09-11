def test_create_and_list(client):
    res = client.post("/tasks", json={"title": "테스트 할 일", "tags": ["개인", "긴급"]})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "테스트 할 일"
    assert {t["name"] for t in body["tags"]} == {"개인", "긴급"}

    res = client.get("/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["tags"]


def test_list_tasks_does_not_n_plus_one(db_session):
    from sqlalchemy import event

    from app.services import task_service

    for i in range(3):
        task_service.create_task(db_session, f"할 일 {i}", [f"태그{i}"])

    queries = []
    engine = db_session.get_bind()

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        tasks = task_service.list_tasks(db_session)
        for task in tasks:
            _ = task.tags
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)

    # selectinload로는 Task 쿼리 1회 + 태그 쿼리 1회, 총 2회 고정.
    # N+1로 되돌아가면 할 일 개수(3)만큼 쿼리가 늘어나 이 값을 넘습니다.
    assert len(queries) <= 2, f"쿼리 {len(queries)}회 발생 (N+1 회귀 의심): {queries}"
