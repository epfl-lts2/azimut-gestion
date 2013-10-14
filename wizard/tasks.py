from celery import task

from wizards import wizs

from wizard.models import Execution


@task(ignore_result=True)
def do_task_step(wizard, exid, taskid, step_data, task_data):
    """Run a task"""

    ex = Execution.objects.get(pk=exid)

    ex.current_task = taskid
    ex.save()

    wiz = wizs[wizard](step_data, task_data)

    (ok, data) = getattr(wiz, 'do_task_' + str(taskid))()

    if ok:
        task_data.append(data)

        if taskid < wiz.get_nb_task():
            do_task_step.delay(wizard, exid, taskid+1, step_data, task_data)
        else:
            ex.current_task = taskid + 1
            ex.done = True
            ex.save()

    else:
        print "Abort " + str(exid) + " at step " + str(taskid)
        ex.done = True
        ex.save()
