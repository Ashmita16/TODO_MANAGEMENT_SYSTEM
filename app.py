import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

def format_date(date_string):
    if not date_string:
        return "N/A"
    try:
        date = datetime.fromisoformat(str(date_string))
        return date.strftime("%d %B %Y, %I:%M %p")
    except ValueError:
        return date_string

st.set_page_config(
    page_title="TODO Management System",
    layout="wide"
)

st.sidebar.title("TODO MANAGEMENT SYSTEM")

option = st.sidebar.selectbox(
    "Select Operation",
    [
        "Home",
        "Create Category",
        "View Categories",
        "Get Category by ID",
        "Update Category",
        "Delete Category",
        "Create Todo",
        "View All Todos",
        "Get Todo by ID",
        "Get Todos by Category",
        "Search & Filter Todos",
        "Update Todo",
        "Delete Todo",
        "Delete All Todos by Category"
    ]
)
if option == "Home":
    st.title("TODO MANAGEMENT SYSTEM")
    st.subheader("API STATUS")

    if st.button("CHECK API STATUS"):
        try:
            response = requests.get(API_URL + "/")
            if response.status_code == 200:
                st.success("FASTAPI IS RUNNING")
                st.json(response.json())
            else:
                st.error("FASTAPI RETURNED AN ERROR")
        except requests.exceptions.ConnectionError:
            st.error("FASTAPI IS NOT RUNNING")

elif option == "Create Category":
    st.title("CREATE CATEGORY")

    name = st.text_input("CATEGORY NAME")
    description = st.text_area("DESCRIPTION")

    if st.button("CREATE CATEGORY"):
        if not name:
            st.warning("Please enter category name")
        elif not description:
            st.warning("Please enter description")
        else:
            data = {
                "name": name,
                "description": description
            }
            try:
                response = requests.post(API_URL + "/categories", json=data)
                if response.status_code == 201:
                    st.success("Category created successfully")
                    data = response.json()
                    st.subheader("Category Details")
                    st.write("**ID:**", data["id"])
                    st.write("**Name:**", data["name"])
                    st.write("**Description:**", data["description"])
                    st.write("**Created At:**", format_date(data["created_at"]))
                    st.write("**Updated At:**", format_date(data["updated_at"]))
                else:
                    st.error(response.json().get("detail", "Something went wrong"))
            except requests.exceptions.ConnectionError:
                st.error("FastAPI is not running")

elif option == "View Categories":
    st.title("VIEW ALL CATEGORIES")

    if st.button("LOAD CATEGORIES"):
        try:
            response = requests.get(API_URL + "/categories")
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    for category in categories:
                        category["created_at"] = format_date(category["created_at"])
                        category["updated_at"] = format_date(category["updated_at"])
                    st.dataframe(categories, use_container_width=True)
                else:
                    st.info("NO CATEGORIES FOUND")
            else:
                st.error(response.json().get("detail", "Error loading categories"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Get Category by ID":
    st.title("GET CATEGORY BY ID")

    category_id = st.number_input("CATEGORY ID", min_value=1, step=1)

    if st.button("GET CATEGORY"):
        try:
            response = requests.get(API_URL + f"/categories/{category_id}")
            if response.status_code == 200:
                st.success("CATEGORY FOUND")
                data = response.json()
                st.write("**ID:**", data["id"])
                st.write("**Name:**", data["name"])
                st.write("**Description:**", data["description"])
                st.write("**Created At:**", format_date(data["created_at"]))
                st.write("**Updated At:**", format_date(data["updated_at"]))
            else:
                st.error(response.json().get("detail", "Category not found"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Update Category":
    st.title("UPDATE CATEGORY")

    category_id = st.number_input("CATEGORY ID", min_value=1, step=1)
    name = st.text_input("NEW NAME")
    description = st.text_area("NEW DESCRIPTION")

    if st.button("UPDATE CATEGORY"):
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description

        if not data:
            st.warning("Enter at least one field to update")
        else:
            try:
                response = requests.put(API_URL + f"/categories/{category_id}", json=data)
                if response.status_code == 200:
                    st.success("Category updated successfully")
                    data = response.json()
                    st.subheader("Updated Category")
                    st.write("**ID:**", data["id"])
                    st.write("**Name:**", data["name"])
                    st.write("**Description:**", data["description"])
                    st.write("**Created At:**", format_date(data["created_at"]))
                    st.write("**Updated At:**", format_date(data["updated_at"]))
                else:
                    st.error(response.json().get("detail", "Error updating category"))
            except requests.exceptions.ConnectionError:
                st.error("FastAPI is not running")


elif option == "Delete Category":
    st.title("DELETE CATEGORY")

    category_id = st.number_input("CATEGORY ID", min_value=1, step=1)

    if st.button("DELETE CATEGORY"):
        try:
            response = requests.delete(API_URL + f"/categories/{category_id}")
            if response.status_code == 200:
                st.success("Category deleted successfully")
                st.json(response.json())
            else:
                st.error(response.json().get("detail", "Error deleting category"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Create Todo":
    st.title("CREATE TODO")

    title = st.text_input("TODO TITLE")
    description = st.text_area("TODO DESCRIPTION")
    priority = st.selectbox("PRIORITY", ["low", "medium", "high"])
    due_date = st.text_input("DUE DATE", placeholder="2026-09-20T18:00:00")
    category_id = st.number_input("CATEGORY ID", min_value=1, step=1)

    if st.button("CREATE TODO"):
        if not title:
            st.warning("Please enter a Todo title")
        elif not description:
            st.warning("Please enter Todo description")
        else:
            data = {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date if due_date else None,
                "category_id": category_id
            }

            try:
                response = requests.post(API_URL + "/todos", json=data)
                if response.status_code == 201:
                    st.success("Todo created successfully")
                    data = response.json()
                    st.subheader("Todo Details")
                    st.write("**ID:**", data["id"])
                    st.write("**Title:**", data["title"])
                    st.write("**Description:**", data["description"])
                    st.write("**Completed:**", data["completed"])
                    st.write("**Priority:**", data["priority"])
                    st.write("**Category ID:**", data["category_id"])
                    st.write("**Category Name:**", data["category_name"])
                    st.write("**Due Date:**", format_date(data["due_date"]))
                    st.write("**Created At:**", format_date(data["created_at"]))
                    st.write("**Updated At:**", format_date(data["updated_at"]))
                else:
                    st.error(response.json().get("detail", "Error creating todo"))
            except requests.exceptions.ConnectionError:
                st.error("FastAPI is not running")

elif option == "View All Todos":
    st.title("VIEW ALL TODOS")

    col1, col2 = st.columns(2)
    with col1:
        page = st.number_input("Page", min_value=1, value=1)
    with col2:
        page_size = st.number_input("Page Size", min_value=1, max_value=100, value=10)

    if st.button("LOAD ALL TODOS"):
        try:
            response = requests.get(API_URL + "/todos", params={"page": page, "page_size": page_size})
            if response.status_code == 200:
                result = response.json()
                st.write(f"**Total Records:** {result['total']} | **Total Pages:** {result['total_pages']}")
                todos = result.get("todos", [])
                if todos:
                    for todo in todos:
                        todo["created_at"] = format_date(todo["created_at"])
                        todo["updated_at"] = format_date(todo["updated_at"])
                        if todo.get("due_date"):
                            todo["due_date"] = format_date(todo["due_date"])
                    st.dataframe(todos, use_container_width=True)
                else:
                    st.info("No Todos found")
            else:
                st.error(response.json().get("detail", "Error fetching todos"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Get Todo by ID":
    st.title("GET TODO BY ID")

    todo_id = st.number_input("Todo ID", min_value=1, step=1)

    if st.button("GET TODO"):
        try:
            response = requests.get(API_URL + f"/todos/{todo_id}")
            if response.status_code == 200:
                st.success("Todo found!")
                data = response.json()
                st.subheader("Todo Details")
                st.write("**ID:**", data["id"])
                st.write("**Title:**", data["title"])
                st.write("**Description:**", data["description"])
                st.write("**Completed:**", data["completed"])
                st.write("**Priority:**", data["priority"])
                st.write("**Category ID:**", data["category_id"])
                st.write("**Category Name:**", data["category_name"])
                st.write("**Due Date:**", format_date(data["due_date"]))
                st.write("**Created At:**", format_date(data["created_at"]))
                st.write("**Updated At:**", format_date(data["updated_at"]))
            else:
                st.error(response.json().get("detail", "Todo not found"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Get Todos by Category":
    st.title("GET TODOS BY CATEGORY")

    category_id = st.number_input("CATEGORY ID", min_value=1, step=1)

    if st.button("GET TODOS"):
        try:
            response = requests.get(API_URL + f"/categories/{category_id}/todos")
            if response.status_code == 200:
                todos = response.json()
                if todos:
                    for todo in todos:
                        todo["created_at"] = format_date(todo["created_at"])
                        todo["updated_at"] = format_date(todo["updated_at"])
                        if todo.get("due_date"):
                            todo["due_date"] = format_date(todo["due_date"])
                    st.dataframe(todos, use_container_width=True)
                else:
                    st.info("No Todos found for this category.")
            else:
                st.error(response.json().get("detail", "Error fetching todos"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Search & Filter Todos":
    st.title("SEARCH & FILTER TODOS")

    search = st.text_input("Search (Title/Description)")
    completed_filter = st.selectbox("Completed Status", ["All", "Completed", "Pending"])
    cat_id_input = st.text_input("Category ID (Optional)")

    if st.button("SEARCH"):
        params = {}
        if search:
            params["search"] = search
        if completed_filter == "Completed":
            params["completed"] = True
        elif completed_filter == "Pending":
            params["completed"] = False
        if cat_id_input.isdigit():
            params["category_id"] = int(cat_id_input)

        try:
            response = requests.get(API_URL + "/todos", params=params)
            if response.status_code == 200:
                result = response.json()
                todos = result.get("todos", [])
                if todos:
                    for todo in todos:
                        todo["created_at"] = format_date(todo["created_at"])
                        todo["updated_at"] = format_date(todo["updated_at"])
                        if todo.get("due_date"):
                            todo["due_date"] = format_date(todo["due_date"])
                    st.dataframe(todos, use_container_width=True)
                else:
                    st.info("No matching todos found")
            else:
                st.error(response.json().get("detail", "Search failed"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Update Todo":
    st.title("UPDATE TODO")

    todo_id = st.number_input("TODO ID", min_value=1, step=1)
    title = st.text_input("NEW TITLE")
    description = st.text_area("NEW DESCRIPTION")
    priority = st.selectbox("NEW PRIORITY", ["No Change", "low", "medium", "high"])
    completed = st.selectbox("COMPLETED STATUS", ["No Change", "True", "False"])
    due_date = st.text_input("NEW DUE DATE", placeholder="2026-09-20T18:00:00")

    if st.button("UPDATE TODO"):
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if priority != "No Change":
            data["priority"] = priority
        if completed != "No Change":
            data["completed"] = True if completed == "True" else False
        if due_date:
            data["due_date"] = due_date

        if not data:
            st.warning("Provide at least one field to update")
        else:
            try:
                response = requests.put(API_URL + f"/todos/{todo_id}", json=data)
                if response.status_code == 200:
                    st.success("Todo updated successfully")
                    st.json(response.json())
                else:
                    st.error(response.json().get("detail", "Update failed"))
            except requests.exceptions.ConnectionError:
                st.error("FastAPI is not running")

elif option == "Delete Todo":
    st.title("DELETE TODO")

    todo_id = st.number_input("TODO ID", min_value=1, step=1)

    if st.button("DELETE TODO"):
        try:
            response = requests.delete(API_URL + f"/todos/{todo_id}")
            if response.status_code == 200:
                st.success("Todo deleted successfully")
                st.json(response.json())
            else:
                st.error(response.json().get("detail", "Error deleting todo"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")

elif option == "Delete All Todos by Category":
    st.title("DELETE ALL TODOS BY CATEGORY")

    category_id = st.number_input("CATEGORY ID", min_value=1, step=1)

    if st.button("DELETE TODOS"):
        try:
            response = requests.delete(API_URL + f"/categories/{category_id}/todos")
            if response.status_code == 200:
                st.success("Todos deleted successfully")
                st.json(response.json())
            else:
                st.error(response.json().get("detail", "Error deleting todos"))
        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running")