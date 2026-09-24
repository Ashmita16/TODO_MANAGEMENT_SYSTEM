from datetime import datetime
from math import ceil
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse,
    Priority
)

app = FastAPI(
    title="TODO MANAGEMENT SYSTEM",
)

categories = []
todos = []

next_category_id = 1
next_todo_id = 1


def get_category_by_id(category_id: int):
    for category in categories:
        if category["id"] == category_id:
            return category
    return None


def get_todo_by_id(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None


def get_category_by_name(name: str):
    for category in categories:
        if category["name"].lower() == name.lower():
            return category
    return None


def format_todo(todo):
    category = get_category_by_id(todo["category_id"])
    return {
        "id": todo["id"],
        "title": todo["title"],
        "description": todo["description"],
        "category_id": todo["category_id"],
        "category_name": category["name"] if category else "Unknown",
        "completed": todo["completed"],
        "priority": todo["priority"],
        "due_date": todo["due_date"],
        "created_at": todo["created_at"],
        "updated_at": todo["updated_at"]
    }


@app.get("/")
def home():
    return {
        "message": "Welcome to Todo Management System"
    }


@app.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=201
)
def create_category(category: CategoryCreate):
    global next_category_id

    existing_category = get_category_by_name(category.name)
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists"
        )

    current_time = datetime.now()
    new_category = {
        "id": next_category_id,
        "name": category.name.strip(),
        "description": category.description,
        "created_at": current_time,
        "updated_at": current_time
    }

    categories.append(new_category)
    next_category_id += 1

    return new_category


@app.get(
    "/categories",
    response_model=list[CategoryResponse]
)
def get_all_categories():
    return categories


@app.get(
    "/categories/{category_id}",
    response_model=CategoryResponse
)
def get_category(category_id: int):
    category = get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@app.put(
    "/categories/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate
):
    category = get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    if category_data.name is not None:
        existing_category = get_category_by_name(category_data.name)
        if existing_category and existing_category["id"] != category_id:
            raise HTTPException(
                status_code=400,
                detail="Another category with this name already exists"
            )
        category["name"] = category_data.name.strip()

    if category_data.description is not None:
        category["description"] = category_data.description

    category["updated_at"] = datetime.now()

    return category


@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    category = get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category_todos = [
        todo
        for todo in todos
        if todo["category_id"] == category_id
    ]

    if category_todos:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot delete category because {len(category_todos)} "
                f"todo(s) belong to it. Delete or move those todos first"
            )
        )

    categories.remove(category)

    return {
        "message": "Category deleted successfully",
        "category_id": category_id
    }


@app.post(
    "/todos",
    response_model=TodoResponse,
    status_code=201
)
def create_todo(todo_data: TodoCreate):
    global next_todo_id
    category = get_category_by_id(todo_data.category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    current_time = datetime.now()

    new_todo = {
        "id": next_todo_id,
        "title": todo_data.title.strip(),
        "description": todo_data.description,
        "category_id": todo_data.category_id,
        "completed": False,
        "priority": todo_data.priority,
        "due_date": todo_data.due_date,
        "created_at": current_time,
        "updated_at": current_time
    }

    todos.append(new_todo)
    next_todo_id += 1

    return format_todo(new_todo)


@app.get(
    "/todos",
    response_model=TodoListResponse
)
def get_all_todos(
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of todos per page"
    ),
    completed: Optional[bool] = Query(
        None,
        description="Filter by completion status"
    ),
    category_id: Optional[int] = Query(
        None,
        description="Filter by category"
    ),
    search: Optional[str] = Query(
        None,
        description="Search in title and description"
    )
):
    filtered_todos = todos.copy()

    if completed is not None:
        filtered_todos = [
            todo
            for todo in filtered_todos
            if todo["completed"] == completed
        ]

    if category_id is not None:
        category = get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )
        filtered_todos = [
            todo
            for todo in filtered_todos
            if todo["category_id"] == category_id
        ]

    if search:
        search_text = search.lower()
        filtered_todos = [
            todo
            for todo in filtered_todos
            if (
                search_text in todo["title"].lower()
                or (
                    todo["description"]
                    and search_text in todo["description"].lower()
                )
            )
        ]

    total = len(filtered_todos)
    total_pages = ceil(total / page_size) if total > 0 else 0

    start = (page - 1) * page_size
    end = start + page_size

    paginated_todos = filtered_todos[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "todos": [format_todo(todo) for todo in paginated_todos]
    }


@app.get("/todos/statistics")
def todo_statistics():
    total = len(todos)

    completed_count = sum(
        1 for todo in todos if todo["completed"]
    )
    pending_count = total - completed_count

    high_priority = sum(
        1 for todo in todos if todo["priority"] == Priority.HIGH
    )
    medium_priority = sum(
        1 for todo in todos if todo["priority"] == Priority.MEDIUM
    )
    low_priority = sum(
        1 for todo in todos if todo["priority"] == Priority.LOW
    )

    return {
        "total_todos": total,
        "completed_todos": completed_count,
        "pending_todos": pending_count,
        "completion_percentage": (
            round((completed_count / total) * 100, 2) if total > 0 else 0
        ),
        "priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        },
        "total_categories": len(categories)
    }


@app.get(
    "/todos/{todo_id}",
    response_model=TodoResponse
)
def get_todo(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return format_todo(todo)


@app.get(
    "/categories/{category_id}/todos",
    response_model=list[TodoResponse]
)
def get_todos_by_category(category_id: int):
    category = get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category_todos = [
        todo for todo in todos if todo["category_id"] == category_id
    ]

    return [format_todo(todo) for todo in category_todos]


@app.put(
    "/todos/{todo_id}",
    response_model=TodoResponse
)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate
):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    if todo_data.title is not None:
        todo["title"] = todo_data.title.strip()

    if todo_data.description is not None:
        todo["description"] = todo_data.description

    if todo_data.category_id is not None:
        category = get_category_by_id(todo_data.category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )
        todo["category_id"] = todo_data.category_id

    if todo_data.completed is not None:
        todo["completed"] = todo_data.completed

    if todo_data.priority is not None:
        todo["priority"] = todo_data.priority

    if todo_data.due_date is not None:
        todo["due_date"] = todo_data.due_date

    todo["updated_at"] = datetime.now()

    return format_todo(todo)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    todos.remove(todo)

    return {
        "message": "Todo deleted successfully",
        "todo_id": todo_id
    }


@app.delete("/categories/{category_id}/todos")
def delete_all_todos_by_category(category_id: int):
    category = get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    global todos
    original_count = len(todos)
    todos = [
        todo for todo in todos if todo["category_id"] != category_id
    ]
    deleted_count = original_count - len(todos)

    return {
        "message": "Todos deleted successfully",
        "category_id": category_id,
        "deleted_count": deleted_count
    }


@app.patch(
    "/todos/{todo_id}/complete",
    response_model=TodoResponse
)
def complete_todo(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    todo["completed"] = True
    todo["updated_at"] = datetime.now()

    return format_todo(todo)


@app.patch(
    "/todos/{todo_id}/pending",
    response_model=TodoResponse
)
def pending_todo(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    todo["completed"] = False
    todo["updated_at"] = datetime.now()

    return format_todo(todo)