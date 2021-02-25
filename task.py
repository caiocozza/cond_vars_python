from collections import deque
from collections.abc import Callable
from typing import Optional
from errors import KeyExistsRegistrationException, KeyNotFound
import threading

class PyTaskManager:
    def __init__(self, concurrent_tasks: int = 1):
        self.__threads = dict()
        self.__actions = dict()
        self.__concurrent_tasks = concurrent_tasks
        self.__task_queue = deque([])
        self.__task_queue_cv = threading.Condition()

        self.__mount_threads()
        self.__start_threads()

    @staticmethod
    def __thread_fn(manager, index: int):
        try:
            manager.__listen()
        except:
            manager.__recreate_thread(index)

    def __listen(self):
        while(True):
            self.__task_queue_cv.acquire()
            scheduled = self.dequeue()

            if scheduled is None:
                self.__task_queue_cv.wait()
                scheduled = self.dequeue()

                if scheduled is not None:
                    if scheduled[0] in self.__actions:
                        self.__actions[scheduled[0]](*scheduled[1])

                    continue
        
            self.__task_queue_cv.release()
            
            if scheduled[0] in self.__actions:
                self.__actions[scheduled[0]](*scheduled[1])

    def __recreate_thread(self, index: int):
        if index in self.__threads:
            self.__threads.pop(index)
        
        thread = threading.Thread(target=self.__thread_fn, args=(self,index,))
        self.__threads.setdefault(index, thread)
        self.__threads[index].start()

    def __mount_threads(self):
        for index in range(self.__concurrent_tasks):
            thread = threading.Thread(target=self.__thread_fn, args=(self,index,))
            self.__threads.setdefault(index, thread)

    def __start_threads(self):
        for index in range(self.__concurrent_tasks):
            if index in self.__threads:
                self.__threads[index].start()

    def register(self, key: str, fn: Callable[[...], str]) -> None:
        if key in self.__actions:
            raise KeyExistsRegistrationException(key)
        else:
            self.__actions.setdefault(key, fn)

    def enqueue(self, key: str, *args) -> None:
        if key not in self.__actions:
            raise KeyNotFound(key)

        with self.__task_queue_cv:
            self.__task_queue.append([key, args])
            self.__task_queue_cv.notify()

    def dequeue(self):
        try:
            return self.__task_queue.popleft()
        except:
            return None


def fn(x, y):
    print(x,y)
    raise Exception("sssssss")

manager = PyTaskManager(3)
manager.register("test", fn)
manager.enqueue("test", 2,3)