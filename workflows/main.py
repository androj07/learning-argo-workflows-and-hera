import os
import uuid

from hera import Task, Workflow, set_global_host, set_global_token, Parameter

argo_token = os.getenv("ARGO_TOKEN")
print(argo_token)
set_global_token(argo_token)
set_global_host("http://localhost:2746")


def say(message: str):
    print(message)


if __name__ == '__main__':
    with Workflow(name=f"dynamic-{uuid.uuid4()}", service_account_name="argo-user") as w:
        # this can be anything! e.g. fetch from some API, then in parallel process all entities; chunk database records
        # and process them in parallel, etc.
        generate_task = Task(
            "generate-1",
            image="generator:local",
            command=["python", "./main.py"],
            args=["--generator", "10"],
            # command=["echo", '[{"value": "a"}, {"value": "b"}, {"value": "c"}]'],
        )
        fanout_task = Task(
            "fanout",
            with_param=generate_task.get_result(),  # this make the task fan out over the `with_param`
            # `inputs` sets the correct input parameter so the result is used
            inputs=[Parameter(name="value", value="{{item.value}}")],
            image="alpine:latest",
            command=["echo", "{{inputs.parameters.value}}"],
        )
        generate_task >> fanout_task

    w.create()
