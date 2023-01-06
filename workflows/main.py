import os

from hera import Task, Workflow, set_global_host, set_global_token

argo_token = os.getenv("ARGO_TOKEN")
print(argo_token)
set_global_token(argo_token)
set_global_host("http://localhost:2746")

def say(message: str):
    print(message)


if __name__ == '__main__':
    with Workflow("global-host") as w:
        a = Task('a', say, ['This is task A!'])
        b = Task('b', say, ['This is task B!'])
        c = Task('c', say, ['This is task C!'])
        d = Task('d', say, ['This is task D!'])

        a >> [b, c] >> d

    w.create()
