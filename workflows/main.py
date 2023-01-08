import os
import sys
import uuid

from hera import Task, Workflow, set_global_host, set_global_token, Parameter, Suspend, ValueFrom

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


if __name__ == '__main__':
    tasks_to_generate = int(sys.argv[1])
    multiplier = int(sys.argv[2])

    with Workflow(name=f"dynamic-{uuid.uuid4()}", service_account_name="argo-user") as w:
        # this can be anything! e.g. fetch from some API, then in parallel process all entities; chunk database records
        # and process them in parallel, etc.
        generate_task = Task(
            "generate-tasks",
            image="generator:local",
            command=["python", "./main.py"],
            args=["--generator", str(tasks_to_generate)],
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
