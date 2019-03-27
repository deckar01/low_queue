from task_queue import TaskQueue

def task_queue(path, debug=False):
    def wrapper(fn):
        class DecoratedQueue(TaskQueue):
            pass
        DecoratedQueue.process = fn
        DecoratedQueue.path = path
        def runner(*work):
            queue = DecoratedQueue(debug)
            queue.push(*work)
            queue.start()
        return runner
    return wrapper

__all__ = ['TaskQueue', 'task_queue']
