import time
from multiprocessing import Process, Lock, Manager, Value
import os

class CoFlow:  

    # ANSI escape codes for colors
    _RED = "\033[91m"
    _GREEN = "\033[92m"
    _YELLOW= "\033[93m"
    _RESET = "\033[0m" # Resets the color to default
    
    def __init__(self):
        """
        Constructor for the CoFlow class.
        """
        manager = Manager()
        self.task_status_dict = manager.dict() # { "task_id" : True/False, .... }
        self.lock = manager.Lock()
        self.task_set = set()
        self.kill_flag = Value('b', False)


    """
    __check_dependency_uniqueness() checks if all the tasks in "dependency_list" have a unique task_id.
    """
    def __check_dependency_uniqueness(self, dependency_list):
        try:
            dep_set = set(dependency_list)
            return len(dep_set) == len(dependency_list)
        except Exception as e:
            print(f"{CoFlow._RED}Error in __check_dependency_uniqueness: {e}{CoFlow._RESET}")
            return False


    """
    __check_uniqueness() checks if all the tasks in "task_list" have a unique task_id.
    returns true, if all the tasks have a unique task_id, otherwise returns false.
    """
    def __check_uniqueness(self, task_list):
        try:
            tset = set()
            for task in task_list:
                if not isinstance(task["task_id"], str):
                    print(f"{CoFlow._RED}Error in {task["task_id"]}: task_id must be a string {CoFlow._RESET}")
                    break
                tset.add(task["task_id"])
            self.task_set = tset
            return len(tset) == len(task_list)
        except Exception as e:
            print(f"{CoFlow._RED}Error in __check_uniqueness: {e}{CoFlow._RESET}")

    """
    
    """
    def __check_cycles(self, task_list):
        try:

            # 1) Creating cycle_check_dict for traversal

            cycle_check_dict = dict()
            
            for task in task_list:
                if(not self.__check_dependency_uniqueness(task["dependency_list"])):
                    print(f"{CoFlow._RED}Error: {task["task_id"]} has duplicate dependencies{CoFlow._RESET}")
                    return False
                task_dependency_set = set(task["dependency_list"])
                if(task["task_id"] in task_dependency_set):
                    print(f"{CoFlow._RED}Error: {task["task_id"]} has a dependency on itself{CoFlow._RESET}")
                    return False
                if(len(task_dependency_set-self.task_set)):
                    print(f"{CoFlow._RED}Error: {task["task_id"]} has a dependency that is not in the task list{CoFlow._RESET}")
                    return False
                cycle_check_dict[task["task_id"]] = task_dependency_set

            print("TASK DEPENDENCY GRAPH:")
            
            # 2) checking for cycles
            level = 0
            while cycle_check_dict:
                # ------- Finding components with zero dependencies ----------
                temp_set = set()
                for t in cycle_check_dict.keys():
                    if(len(cycle_check_dict[t])==0):
                        temp_set.add(t)
                if(len(temp_set)==0):
                    break
                
                # ------- Removing those from component dependencies of other components -----------
                for t in cycle_check_dict.keys():
                    cycle_check_dict[t] = cycle_check_dict[t] - temp_set
                
                # ------- Removing their entry from cycle_check_dict -----------------
                for t in temp_set:
                    del cycle_check_dict[t]
                print(f"L{level}: {temp_set}")
                level += 1

            if(len(cycle_check_dict)==0):
                return True
            else:
                return False
                
        except Exception as e:
            print(f"{CoFlow._RED}Error in __check_cycles: {e}{CoFlow._RESET}")



    """
    __dependency_check() checks if all the tasks in "dependency_list" have been completed.
    returns true, if all the tasks have been completed, otherwise returns false.
    """
    def __dependency_check(self, task: dict):
        try:
            flag = True
            dependency_list = task["dependency_list"]
            for upstream_task in dependency_list:
                flag = flag and self.task_status_dict[upstream_task]
            return flag
        except Exception as e:
            print(f"{CoFlow._RED}Error in dependency_check for {task['task_id']}: {e}{CoFlow._RESET}")
            with self.lock:
                self.kill_flag.value = True
            return False


    """
    _run_one_flow() runs the function task["function_handle"] with arguments task["function_args"]
    once the function is executed, it set the value of task_status_dict[task["task_id"]] to True, 
    indicating that the task has been completed.
    """
    def __run_one_flow(self, task):

        try:
            # 1) while loop that runs untill all dependencies are satisfied
            while (not self.__dependency_check(task) and not self.kill_flag.value):
                time.sleep(2)

            # 2) trigger the flow.
            if not(self.kill_flag.value):
                print("Triggered: ",task["task_id"]," :: ",task["function_handle"].__name__,"(",*task["function_args"],")")
                #print(f"Triggered: {task['task_id']} :: {task['function_handle'].__name__}({*task['function_args']})")
                task["function_handle"](*task["function_args"])
                with self.lock:
                    self.task_status_dict[task["task_id"]] = True
                print("Completed: ",task["task_id"])
            else:
                print(f"{CoFlow._YELLOW}Did Not Run {task['task_id']} {CoFlow._RESET}")

        except Exception as e:
            print(f"{CoFlow._RED}Error while running task {task['task_id']}: {e}{CoFlow._RESET}")
            with self.lock:
                self.kill_flag.value = True


    """
    trigger_co_flow() runs all the tasks in task_list parallely.
    """
    def trigger_co_flow(self, 
                        task_list: list):
        """
        task_list = [
                        { task_id: str,
                          function_handle: function_handle,
                          function_args: function_args,
                          task_dependencies: list
                        }, ....
                    ]
        """

        try:
            # 1) checking if all the tasks in task_list have a unique task_id
            if(not self.__check_uniqueness(task_list)):
                print(f"{CoFlow._RED}\nError: All tasks must have unique task_id{CoFlow._RESET}")
                return
            print(f"{CoFlow._GREEN}\nTask uniqueness check passed{CoFlow._RESET}")
            print("-------------------------")

            # 2) checking if there are no cycles in the task_list
            if(not self.__check_cycles(task_list)):
                print(f"{CoFlow._RED}Error: Cycle check failed{CoFlow._RESET}")
                return
            print(f"{CoFlow._GREEN}Cycle check passed{CoFlow._RESET}")
            print("-------------------------")
            
            # 3) initializing the task_status_dict dictionary
            for task in task_list:
                self.task_status_dict[task["task_id"]] = False
            
            # 4) Run a loop over task_list and trigger each task.
            pid = os.getpid()

            print(f"{CoFlow._YELLOW}PARENT PROCESS ID: {pid}{CoFlow._RESET}")
            processes = []
            
            for task in task_list:
                p = Process(target=self.__run_one_flow, args=(task,))
                processes.append(p)
                p.start()  # Start the process
                #print("Created process for: ",task["task_id"])
            
            print(f"{CoFlow._GREEN}All processes are dispatched. Waiting for them to complete...{CoFlow._RESET}")
            
            # join() to wait for all processes to complete
            for p in processes:
                p.join() # This will block the main process until p completes
            
            print("-------------------------")
            if(self.kill_flag.value):
                print(f"{CoFlow._RED}One of the tasks failed. Please check your task graph.{CoFlow._RESET}\n")
            else:
                print(f"{CoFlow._GREEN}All parallel processes have completed.{CoFlow._RESET}\n")

        except Exception as e:
            print(f"\n{CoFlow._RED}Error: {e}{CoFlow._RESET}")
        
        