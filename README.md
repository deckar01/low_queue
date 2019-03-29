# 🔅 low_queue

A low maintenance task queue for python.

## Status

🔬 This code is experimental. User discretion is advised.

## Dependencies

- A unix-based operating system

## Design

- Persistence: [`sqlite3`](https://docs.python.org/3/library/sqlite3.html)
- Serialization: [`pickle`](https://docs.python.org/3/library/pickle.html)
- Processing: [`os.fork()`](https://docs.python.org/3/library/os.html#os.fork)

## Usage

### @task_queue(path, log_level=ERROR)

A decorator interface for pushing work and running tasks. Calling the decorated
method creates a `TaskQueue` instance, calls `TaskQueue.push()`, then calls
`TaskQueue.start()`.

- **Decorator Arguments**
    - **path** `String` - See `TaskQueue.path`.
    - **log_level** `Boolean` - Optional. See `TaskQueue()`.
- **Function Arguments**
    - **queue** `TaskQueue` - A reference to the `TaskQueue` instance.
    - **work** `Object` - See `TaskQueue.process()`.

**Example**

```py
from low_queue import task_queue, TaskQueue
import time


@task_queue('./test.db', log_level=TaskQueue.INFO)
def test_queue(queue, work):
    # Do slow stuff here.
    time.sleep(2)
    queue.info(work, 'done')

if __name__ == '__main__':
    test_queue(1, 2, 3)
    test_queue(3, 4, 5)
```

### TaskQueue

A class that stores tasks and processes them as soon as possible. This acts as
both the client for requesting tasks and the worker for executing tasks.

#### TaskQueue.path

An SQLite path used to persist the backlog of tasks. This property must be
defined in a subclass.

#### TaskQueue(log_level=ERROR)

- **Arguments**
    - **log_level** `Boolean` - Prints a log of all activity. Defaults to only
      print errors. Options are `ERROR`, `WARN`, `INFO`, and `NONE`. These flags
      are static attributes of the `TaskQueue` class.

#### TaskQueue.process(work)

Perform the task. This method must be implemented in a subclass.

- **Arguments**
- **work** `Object` - The data required for the process to execute.

#### TaskQueue.push(work, ...)

Takes data that needs to be processed and adds it to the queue. Multiple tasks
can be queued in a single call by passing additional arguments. If the data is
already in the queue it will not be added again.

- **Arguments**
    - **work** `Object` - Data required to execute a specific process.

#### TaskQueue.start()

Start a worker process to execute tasks unless one is already active. The
current process forks, detaches, and processes the queue until it is empty. This
allows the calling process to continue and exit immediately.

#### TaskQueue.error(message, ...)

Output an error message. Additional messages are separated by spaces.

- **Arguments**
    - **message** `String` - The message to print.

#### TaskQueue.warn(message, ...)

Output a warning message. Additional messages are separated by spaces.

- **Arguments**
    - **message** `String` - The message to print.

#### TaskQueue.info(message, ...)

Output a message. Additional messages are separated by spaces.

- **Arguments**
    - **message** `String` - The message to print.

#### TaskQueue.ERROR

A flag that indicates that only error messages should be logged.

#### TaskQueue.WARN

A flag that indicates that warning and error messages should be logged.

#### TaskQueue.INFO

A flag that indicates that all messages should be logged.

#### TaskQueue.SILENT

A flag that indicates that no messages should be logged.

**Example**

```py
from low_queue import TaskQueue
import time


class TestQueue(TaskQueue):
    path = './test.db'

    def test_queue(self, work):
        # Do slow stuff here.
        time.sleep(2)
        queue.info(work, 'done')

if __name__ == '__main__':
    queue = TestQueue(log_level=TaskQueue.INFO)
    queue.push(1, 2, 3)
    queue.push(3, 4, 5)
    queue.start()
```

## Warnings

- The work pushed to the queue must be ordered and deterministic to ensure
  duplicate tasks are not created.
- No record of completed work is maintained. Side effects of the task must be
  used to determine the state of the task.

## Development

### TODO

- Add tests.
