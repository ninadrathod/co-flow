import time

def sleep_function(seconds):
    """
    A function that sleeps for a given number of seconds.
    It prints the process ID and the sleep duration.
    """
    time.sleep(seconds)
   
"""
task_list stores all the tasks to be executed.
"""
task_list = [
        {
            "task_id": "t1",
            "function_handle": sleep_function,
            "function_args": [20],
            "dependency_list": []        
        },
        {
            "task_id": "t2",
            "function_handle": sleep_function,
            "function_args": [4],
            "dependency_list": ["t1"]        
        },
        {
            "task_id": "t3",
            "function_handle": sleep_function,
            "function_args": [1],
            "dependency_list": ["t1"]        
        },
        {
            "task_id": "t4",
            "function_handle": sleep_function,
            "function_args": [3],
            "dependency_list": ["t2"]        
        },
        {
            "task_id": "t5",
            "function_handle": sleep_function,
            "function_args": [3],
            "dependency_list": []        
        },
        {
            "task_id": "t6",
            "function_handle": sleep_function,
            "function_args": [4],
            "dependency_list": ["t4","t5"]        
        }
    ]