from typing import Optional

from aiohttp.web import json_response
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from snapper.task import Task
from snapper.task_history import TaskHistory
from snapper.task_redirect import TaskRedirect
from snapper.task_snapper import TaskSnapper

TASKS = {}


class SubmitResource:
    @staticmethod
    async def post(request: Request) -> Response:
        data = await request.json()
        app = request.app

        if "urls" not in data:
            return json_response({"message": "'urls' not specified"}, status=400)

        new_task = TaskSnapper(
            urls=data["urls"],
            timeout=app["timeout"],
            user_agent=app["user_agent"],
            output=app["output_dir"],
            phantomjs_binary=app["phantomjs_binary"],
            output_paths_format=app['output_paths_format'],
            task_timeout_sec=app['task_timeout_sec'],
        )
        TASKS[new_task.id] = new_task
        new_task.run()

        return json_response(new_task.to_dict(), status=200)


class SubmitRedirectResource:
    @staticmethod
    async def post(request: Request) -> Response:
        data = await request.json()
        app = request.app

        if "urls" not in data:
            return json_response({"message": "'urls' not specified"}, status=400)

        new_task = TaskRedirect(
            urls=data["urls"],
            timeout=app["timeout"],
            user_agent=app["user_agent"],
            chromedriver_binary=app["chromedriver_binary"],
            task_timeout_sec=app['task_timeout_sec'],
        )
        TASKS[new_task.id] = new_task
        new_task.run()

        return json_response(new_task.to_dict(), status=200)

class HistoryResource:
    @staticmethod
    async def post(request: Request) -> Response:
        data = await request.json()
        app = request.app

        if "urls" not in data:
            return json_response({"message": "'urls' not specified"}, status=400)

        new_task = TaskHistory(
            urls=data['urls'],
            output=app['output_dir'],
            output_paths_format=app['output_paths_format'],
            task_timeout_sec=app['task_timeout_sec'],
        )
        TASKS[new_task.id] = new_task
        new_task.run()

        return json_response(new_task.to_dict(), status=200)

class TaskResource:
    @staticmethod
    def load_task(task_id: str) -> Optional[Task]:
        return TASKS.get(task_id)

    @staticmethod
    def delete_task(task_id: str):
        del TASKS[task_id]

    @staticmethod
    async def get(request: Request) -> Response:
        task_id = request.match_info.get('task_id')
        task = TaskResource.load_task(task_id)
        if task is None:
            return json_response({"message": "no such task"}, status=404)
        return json_response(task.to_dict(), status=200)

    @staticmethod
    async def delete(request: Request) -> Response:
        task_id = request.match_info.get('task_id')
        TaskResource.delete_task(task_id)
        return json_response("", status=204)


class TaskListResource:
    @staticmethod
    async def get(request: Request) -> Response:
        return json_response([task.to_dict() for task in TASKS.values()])


def setup_routes(app: Application) -> None:
    app.router.add_post("/api/v1/submit", SubmitResource.post)
    app.router.add_post("/api/v1/redirects", SubmitRedirectResource.post)
    app.router.add_post("/api/v1/history", HistoryResource.post)
    app.router.add_get("/api/v1/tasks", TaskListResource.get)
    app.router.add_get('/api/v1/tasks/{task_id}', TaskResource.get)
    app.router.add_delete('/api/v1/tasks/{task_id}', TaskResource.delete)
