# 🔅 low_queue

A low maintenance task queue for python.

## Status

🔬 This code is experimental. User discretion is advised.

## Dependencies

- A unix-based operating system

## Design

- Persistence: [`sqlite3`](https://docs.python.org/3/library/sqlite3.html)
- Serialization: [`json`](https://docs.python.org/3/library/json.html)
- Processing: [`os.fork()`](https://docs.python.org/3/library/os.html#os.fork)

## Usage

### @task_queue(path, debug=False)

A decorator interface for pushing work and running tasks. Calling the decorated
method creates a `TaskQueue` instance, calls `TaskQueue.push()`, then calls
`TaskQueue.start()`.

- **Decorator Arguments**
    - **path** `String` - See `TaskQueue.path`.
    - **debug** `Boolean` - Optional. See `TaskQueue()`.
- **Function Arguments**
    - **queue** `TaskQueue` - A reference to the `TaskQueue` instance.
    - **work** `Object` - See `TaskQueue.process()`.

**Example**

```py
from low_queue import task_queue
import time


@task_queue('./test.db', debug=True)
def test_queue(queue, work):
    # Do slow stuff here.
    time.sleep(2)
    queue.log(work, 'done')

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
defined in a subclass.

#### TaskQueue(debug=False)

- **Arguments**
    - **debug** `Boolean` - Prints a log of all activity. Defaults to `False`.

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

**Example**

```py
from low_queue import TaskQueue
import time


class TestQueue(TaskQueue):
    path = './test.db'

    def test_queue(self, work):
        # Do slow stuff here.
        time.sleep(2)
        queue.log(work, 'done')

if __name__ == '__main__':
    queue = TestQueue(debug=True)
    queue.push(1, 2, 3)
    queue.push(3, 4, 5)
    queue.start()
```

## Warnings

- The work pushed to the queue must be ordered and deterministic to ensure
  duplicate tasks are not created.
- No record of completed work is maintained. The side effects of the task
  must be used to indicate the state of the task.
- There is a narrow window of time between the queue being empty and a worker
  indicating that it is no longer active that new data could be added to the
  queue. During this time new workers would not be able to start and work would
  remain in the queue until the next attempt to start a worker. I have not
  observed this, but it seems possible. This can be mitigated by retrying jobs
  that have not completed when their resources are requested and found to be
  missing. Another solution would be to configure the system to start a worker
  on an interval via a cron job.

## Development

### TODO

- Add tests.
- Make the backlog read and the status write an atomic transaction.
