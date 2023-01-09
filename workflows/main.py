import os
import sys
import time
import uuid

from hera import Task, Workflow, set_global_host, set_global_token, Parameter, ValueFrom

argo_token = os.getenv("ARGO_TOKEN")
print(argo_token)
set_global_token(argo_token)
set_global_host("http://localhost:2746")


def say(message: str):
    print(message)


def fanin(values: list):
    sum = 0
    for val in values:
        sum += int(val["value"])
    print(f"Received values: {values}!")
    print(f"Total: {sum}!")


def create_workflow(tasks: int, multiplier: int):
    with Workflow(name=f"dynamic-{uuid.uuid4()}", service_account_name="argo-user") as w:
        # this can be anything! e.g. fetch from some API, then in parallel process all entities; chunk database records
        # and process them in parallel, etc.
        generate_task = Task(
            "generate-tasks",
            image="generator:local",
            command=["python", "./main.py"],
            args=["--generator", str(tasks)],
            # command=["echo", '[{"value": "a"}, {"value": "b"}, {"value": "c"}]'],
        )
        fanout_task = Task(
            "multiply-values",
            with_param=generate_task.get_result(),  # this make the task fan out over the `with_param`
            # `inputs` sets the correct input parameter so the result is used
            inputs=[Parameter(name="value", value="{{item.value}}")],
            image="generator:local",
            command=["python", "./main.py"],
            outputs=[Parameter("value", value_from=ValueFrom(path="/tmp/value"))],
            args=["--multiply", str(multiplier), "{{inputs.parameters.value}}"],
        )
        fanin_task = Task(
            "fanin",
            fanin,
            inputs=[fanout_task.get_parameters_as("values")])
        generate_task >> fanout_task >> fanin_task

    w.create()
    print("Generated workflow\n")


if __name__ == '__main__':
    number_of_workflows = int(sys.argv[1])
    tasks_to_generate = int(sys.argv[2])
    multiplier = int(sys.argv[3])
    for i in range(number_of_workflows):
        create_workflow(tasks_to_generate, multiplier)
        time.sleep(1)