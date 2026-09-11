from sqlalchemy.orm import Session

from app.models import Tag, Task


def list_tasks(db: Session) -> list[Task]:
    # 버그: 태그를 즉시 로딩하지 않습니다.
    # 응답을 직렬화할 때 각 할 일의 task.tags에 접근하면 태그 조회 쿼리가
    # 할 일 개수만큼 추가로 실행됩니다(N+1). 할 일이 늘수록 GET /tasks 가 느려집니다.
    #
    # 수정 방향:
    #   from sqlalchemy.orm import selectinload
    #   tasks = db.query(Task).options(selectinload(Task.tags)).all()
    tasks = db.query(Task).all()
    return tasks


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, title: str, tag_names: list[str]) -> Task:
    tags: list[Tag] = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)

    task = Task(title=title, tags=tags)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
