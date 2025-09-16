# CoFlow: Parallel Process Execution 🚀

**CoFlow** is a Python project designed to simplify the execution of tasks in parallel using a custom class. It helps you manage and trigger processes concurrently, which can significantly speed up your workflows.

***

## How It Works

The core of the project is the `CoFlow` class. It takes a list of tasks, manages their dependencies, and executes them in parallel.

### 1. Define Your Tasks

Tasks are defined as a list of dictionaries. Each dictionary represents a single task and should contain the following keys:

-   `task_id` (`str`): A unique identifier for the task.
-   `function_handle` (`function`): A handle to the function you want to execute.
-   `function_args` (`list`): A list of arguments to pass to the function.
-   `task_dependencies` (`list`): A list of `task_id`s that must be completed before this task can run.

Refer to **`input.py`** for a clear example of how to structure this list.

### 2. Trigger Parallel Execution

Once your task list is prepared, pass it to the `trigger_co_flow()` function, using the `CoFlow` class object. The project automatically handles the creation of worker processes and ensures that tasks are executed in the correct order based on their dependencies.

For a complete demonstration of how to use the `trigger_co_flow()` function and how to set up your tasks, please see **`demonstration.py`** or run **`$python3 demonstration.py`**.
