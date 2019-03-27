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
