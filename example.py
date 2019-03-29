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
