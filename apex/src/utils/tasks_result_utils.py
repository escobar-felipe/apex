class TaskStatusSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskStatusSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.task_status = {}

    def set_status(self, task_id, status):
        self.task_status[task_id] = status

    def get_status(self, task_id):
        return self.task_status.get(task_id)

    def compare_status(self, task_id, async_result):
        current_status = self.get_status(task_id)
        if current_status == async_result:
            return True #igual
        else:
            return False #difente

    def has_id(self, task_id):
        return task_id in self.task_status

task_status_singleton = TaskStatusSingleton()