from typing import List, Optional

from flask import request, Response
from flask import jsonify, make_response
from flask_restful import Resource

from snapper import app, api
from snapper.task import Task

TASKS = {}


class SubmitResource(Resource):

    @staticmethod
    def create_task(urls: List[str]) -> Task:
        new_task = Task(
            urls=urls,
            timeout=app.config["timeout"],
            user_agent=app.config["user_agent"],
            output=app.config["output_dir"],
            phantomjs_binary=app.config["phantomjs_binary"]
        )
        TASKS[new_task.id] = new_task
        return new_task

    def post(self) -> Response:
        if "urls" not in request.json:
            return make_response(
                jsonify({"message": "'urls' not specified"}), 400)

        new_task = self.create_task(request.json.get("urls"))
        new_task.run(num_workers=app.config["num_workers"])
        return jsonify(new_task.to_dict())


class TaskResource(Resource):
    @staticmethod
    def load_task(task_id: str) -> Optional[Task]:
        return TASKS.get(task_id)

    @staticmethod
    def delete_task(task_id: str):
        # Let's keep files on disk for now
        # shutil.rmtree(TASKS[task_id].output_path)
        del TASKS[task_id]

    def get(self, task_id: str) -> Response:
        task = self.load_task(task_id)
        if task is None:
            return make_response(
                jsonify({"message": "no such task"}), 404)
        return jsonify(task.to_dict())

    def delete(self, task_id: str) -> Response:
        self.delete_task(task_id)
        return Response(
            "",
            status=204,
            mimetype='application/json'
        )


class TaskListResource(Resource):

    def get(self) -> Response:
        return jsonify([task.to_dict() for task in TASKS.values()])


api.add_resource(SubmitResource, '/api/v1/submit')
api.add_resource(TaskListResource, '/api/v1/tasks')
api.add_resource(TaskResource, '/api/v1/tasks/<task_id>')
