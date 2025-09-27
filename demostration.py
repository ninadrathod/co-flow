from CoFlow import CoFlow
import input


if __name__ == "__main__":
    task_list = input.task_list
    cf_obj = CoFlow()
    cf_obj.trigger_co_flow(task_list,2)
    