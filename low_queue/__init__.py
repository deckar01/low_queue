from task_queue import TaskQueue

def task_queue(path, log_level=1):
    def wrapper(fn):
        class DecoratedQueue(TaskQueue):
            pass
        DecoratedQueue.process = fn
        DecoratedQueue.path = path
        def runner(*work):
            queue = DecoratedQueue(log_level)
            queue.push(*work)
            queue.start()
        return runner
    return wrapper

__all__ = ['TaskQueue', 'task_queue']
