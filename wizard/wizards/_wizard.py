
class _Wizard():
    """A basic wizard"""

    _name = ''
    _description = ''

    _nb_step = 1
    _nb_task = 1

    _steps_names = ['Example']
    _tasks_names = ['Example']

    ### Functions to implement
    def display_step_1(self, request):
        """Must return a (text, form, js) for the step 1"""
        pass

    def save_step_1(self, form):
        """Called when the form is valid. Must return elements to save a the step. Must be serializable ! Data will be available as self.step_data[id]"""
        pass

    def do_task_1(self):
        """Called to execute task 1. Must return (True, TaskData) if the task was successfull, (False, None) otherwhise. Data will be available as self.task_data[id]"""
        pass

    ### Internal functions

    def __init__(self, step_data, task_data):

        self.step_data = step_data
        self.task_data = task_data

    def get_name(self):
        """Return the name of the wizard"""
        return self._name

    def get_description(self):
        """Return the description of the wizard"""
        return self._description

    def get_nb_step(self):
        """Return the number of step of the wizard"""
        return self._nb_step

    def get_nb_task(self):
        """Return the number of task of the wizard"""
        return self._nb_task

    def get_steps_name(self):
        """Return the name for differents steps of the wizard"""
        return self._steps_names[:]

    def get_tasks_name(self):
        """Return the name for differents tasks of the wizard"""
        return self._tasks_names[:]
