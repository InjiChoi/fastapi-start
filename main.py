from typing import List
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, validator

app = FastAPI()

class Todo(BaseModel):
    id: int
    title: str
    date: str
    done: bool = False

    @validator("title")
    def title_length_under_20(cls, v):
        if len(v) > 25:
            raise ValueError("must be under 20")
        return v

class Todos(BaseModel):
    todos: List[Todo]

model = Todos(
    todos = [    
        Todo(id=1, title="저녁먹기", date= "20220706"),
        Todo(id=2, title="숙제봐주기", date= "20220706"),
        Todo(id=3, title="일하기", date= "20220706")
    ]
)

# todos = [
#     Todo(id=1, title="저녁먹기", date= "20220706"),
#     Todo(id=1, title="숙제봐주기", date= "20220706"),
#     Todo(id=1, title="일하기", date= "20220706")

#     # {"id":1, "title": "저녁먹기", "date": "20220706", "done": False},
#     # {"id":2, "title": "숙제봐주기", "date": "20220707", "done": False},
#     # {"id":3, "title": "일하기", "date": "20220706", "done": True},

# ]

@app.get("/")
async def root():
    return {"msg": "hello world"}

@app.post("/posts", response_model=List[Todo])
async def add_todo_item(title:str, date:str): # body로 받을 수도 있고 param으로 받을 수도 있음
    _id = str(max([t.get("id") for t in model.todos]) + 1)
    _todo = Todo(id=_id, title=title, date=date)
    model.todos.append(_todo)
    # _id = max([t.get("id") for t in todos]) + 1
    # _todo = {"id": _id, "title": title, "date": date, "done": False}
    # todos.append(_todo)
    return _todo
    # return {"title": title, "date": date}

@app.get("/todos", response_model=List[Todo])
async def get_todo_list():
    return model.todos
    # return todos
    # return {}

async def get_todo_item(todo_id: str):
    _todos = [t for t in model.todos if str(t.id) == todo_id]
    if len(_todos) != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Not found todo item")
    return _todos[0]

# Depends
# id를 가지고 todo를 가져오는 fn
# todo done의 값만 가지고 싶다.

async def get_done(todo: Todo = Depends(get_todo_item)):
    return todo.done

@app.get("/todos/{todo_id}/done", response_model=Todo)
async def is_done(done:bool=Depends(get_done)):
    return {"done": done}


@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo_item(todo: Todo = Depends(get_todo_item)):
    return todo

@app.delete("/todos/{todo_id}")
async def delete_todo_item(todo: Todo = Depends(get_todo_item)):
    # return {"todo_id":todo_id}
    return todo

@app.patch("/todos/{todo_id}")
async def update_todo_title(title:str, todo: Todo = Depends(get_todo_item)): # title은 param으로 받음
    todo.title = title
    # 리스트 바꿔치기해서 저장
    return todo
    # return {"todo_id":todo_id, "title": title}