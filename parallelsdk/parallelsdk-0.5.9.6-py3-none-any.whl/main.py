import json
import os
import random
import numpy as np

from parallelsdk.data_toolbox.data_toolbox import *
from parallelsdk.mp_toolbox.mp_toolbox import *
from parallelsdk.mp_toolbox.mp_model import *
from parallelsdk.routing_toolbox.routing_toolbox import *
from parallelsdk.cp_toolbox.cp_toolbox import *
from parallelsdk.scheduling_toolbox.SchedulingModels.Employee import Employee
from parallelsdk.scheduling_toolbox.SchedulingModels.Staff import Staff
from parallelsdk.scheduling_toolbox.scheduling_toolbox import *
from parallelsdk.deployment.deployment_model import *
from parallelsdk.client import *
from parallelsdk.test.smart_grid_cp_model import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def createVRPModel(vrp):
    np.random.seed(1)
    depot_loc = np.random.uniform(0.0, 10.0, size=(2,))
    vrp.AddDepot(depot_loc)
    delivery_loc = []
    for k in range(9):
        delivery = np.random.uniform(0.0, 10.0, size=(2,))
        delivery_loc.append(delivery)
        vrp.AddLocation(position=delivery, demand=random.randint(5, 10))

    # vrp.AddVehicle( name="vehicle_%d" %(1), load=0.0, capacity=300)
    for k in range(3):
        vrp.AddVehicle(name="vehicle_%d" % k, load=0.0, capacity=15)
    vrp.InferDistanceMatrix()
    return vrp


def createMappedVRPModel(vrp):
    # vrp.AddDepot("145 Concord Rd Wayland, MA 01778")
    depot_loc = np.random.uniform(0.0, 10.0, size=(2,))
    depot_loc[0] = 42.35813
    depot_loc[1] = -71.06288
    vrp.AddDepot(depot_loc)
    # Use random integer for demand: random.randint(5, 10)
    vrp.AddLocation("13 Lincoln Rd Wayland, MA 01778", demand=0, location_id=0)
    vrp.AddLocation("662 Boston Post Rd, Weston, MA 02493", demand=0, location_id=1)
    vrp.AddLocation("2345 Commonwealth Avenue, Newton, MA 02466", demand=0, location_id=2)
    vrp.AddLocation("180 Hemenway Rd, Framingham, MA 01701", demand=0, location_id=3)
    vrp.AddLocation("72 Wayside Inn Rd, Sudbury, MA 01776", demand=0, location_id=4)
    vrp.AddLocation("22 Flutie Pass, Framingham, MA 01701", demand=0, location_id=5)
    vrp.AddLocation("208 S Great Rd, Lincoln, MA 01773", demand=0, location_id=6)
    vrp.AddLocation("9 Hope Ave, Waltham, MA 02453", demand=0, location_id=7)
    vrp.InferDistanceMatrix(metric='maps', API_key='AIzaSyCGOa79k466MIwCERz5_obRhmONuebj5Cs')
    for k in range(3):
        vrp.AddVehicle(name="vehicle_%d" % k, load=0.0, capacity=2147483647) #30
    return vrp


def createSchedulingModel(scheduler):
    model = scheduler.get_instance()
    team = Staff("Team", "575.123.4567", "TruckBest")
    mario = Employee("Mario", "M", "587.234.1543", "TruckBest", "Boston")
    john = Employee("John", "M", "878.232.5873", "TruckBest", "Boston")
    team.add_staff_member(mario, 100)
    team.add_staff_member(john, 100)
    team.add_shift_preference(1, 0, 10)
    model.set_schedule_num_days(5)
    model.set_shift_per_day(3)
    model.add_staff(team)


def createMPModel(model):
    inf = Infinity()
    x = model.IntVar(0.0, inf, 'x')
    y = model.IntVar(0.0, inf, 'y')
    # print(x)
    # print(y)
    c1 = model.Constraint(x + 7 * y <= 17.5)
    c2 = model.Constraint(x <= 3.5)
    model.Objective(x + 10 * y, maximize=True)


def createJobShopModel(job_shop):
    js = job_shop.get_instance()
    js.set_search_timeout(10.0)
    js.set_num_parallel_cores(1)
    machine = js.add_machine(1)
    machine.add_time_window_availability(32, 54)
    job_1 = js.add_job(0)
    job_2 = js.add_job(1)
    job_2.add_dependency(job_1.get_id())
    task_1 = job_1.add_task(0)
    task_1.set_required_machine(machine.get_id())
    task_2 = job_2.add_task(1)
    task_2.set_required_machine(machine.get_id())
    task_1.set_duration(5)
    task_2.set_duration(5)


def createJobShopModelFromData(js):
    path_res = "data/res.json"
    path_task = "data/task.json"
    with open(path_res, encoding='utf-8-sig') as json_file:
        text = json_file.read()
        res_data = json.loads(text)
    with open(path_task, encoding='utf-8-sig') as json_file:
        text = json_file.read()
        task_data = json.loads(text)

    scaling_factor = 10
    res_list = res_data['res']
    for res in res_list:
        machine_id = res['id']
        machine = js.add_machine(machine_id, 'machine_' + str(machine_id))
        periods = res['periods']
        for period in periods:
            machine.add_time_window_availability(int(period['s'] * scaling_factor), int(period['e'] * scaling_factor))

    task_list = task_data['tasks']
    for task in task_list:
        job_id = task['id']
        job = js.add_job(job_id, 'job_' + str(job_id))
        job_task = job.add_task(job_id)
        required_machine = task['res'][0]
        task_duration = int(task['dur'] * scaling_factor)
        job_task.set_required_machine(required_machine)
        job_task.set_duration(task_duration)
        for dep in task['dep']:
            if dep > -1:
                job.add_dependency(dep)


def createCPModel(model):
    x = model.IntVar(0, 10, 'x')
    y = model.IntVar(0, 10, 'y')
    print(x.to_string())
    print(y.to_string())
    # model.Constraint(x != y)
    c = model.AllDifferent([x, y])
    print(c.to_string())
    model.set_objective(y, minimize=False)


def createPythonFunctionTool(tool):
    python_fcn = tool.get_instance()
    python_fcn.add_entry_fcn_name("myFcn")
    python_fcn.add_entry_module_name("my_file")
    python_fcn.add_input_argument(3, "int")
    python_fcn.add_input_argument([3.14, 4.15], "double")
    python_fcn.clear_input_arguments()
    python_fcn.add_input_argument(5)
    python_fcn.add_input_argument(6)
    python_fcn.add_output_argument("int", False)
    python_fcn.add_output_argument("bool", True)

    # Add the path to the test folder
    path_str = str(os.path.join(os.path.dirname(__file__), "test"))
    python_fcn.add_environment_path(path_str)
    return tool


def verifyJobShop(js):
    job_list = js.get_all_jobs()
    machine_list = js.get_all_machines()
    model_consistency = True
    scaling_factor = 1

    # Store of the tasks into a map, just for convenience
    task_map = {}
    for job in job_list:
        jtask = job.get_task_list()[0]
        task_map[jtask.get_id()] = jtask

    # Check start/end times for task dependencies
    for job in job_list:
        # For each job, get the task and its start time
        curr_task_start = (job.get_task_list()[0]).get_start_time()
        dep_list = job.get_dependency_list()
        for dep in dep_list:
            # For each dependency, check if the dependency finishes befor this job starts
            jtask = task_map[dep]
            dep_end_time = jtask.get_start_time() + jtask.get_duration()
            if curr_task_start < dep_end_time:
                model_consistency = False
                print('Error: current Job', job.get_id(), "starts at", curr_task_start / scaling_factor,
                      "and depends on", dep, "finishing at", dep_end_time / scaling_factor)

    # Check machine execution list
    for machine in machine_list:
        # For each machine, get its availabilities and its schedule
        schedule = machine.get_schedule()
        window_availability = machine.get_time_window_availabilities()
        for scheduled_task in schedule:
            task_id = scheduled_task[0]
            task_start = scheduled_task[1]
            task_end = scheduled_task[2]
            # Check that tasks are scheduled on the required machines
            if task_map[task_id].get_required_machine() != machine.get_id():
                model_consistency = False
                print('Error: task', task_id, "should be scheduled on", task_map[task_id].set_required_machine(),
                      "and it is scheduled on", machine.get_id())
            # Check that tasks start when the machine is available
            found_window = False
            for window in window_availability:
                if task_start >= window[0] and task_end <= window[1]:
                    found_window = True
                    break
            if not found_window:
                model_consistency = False
                print('Error: task', task_id, "scheduled at", task_start / scaling_factor, task_end / scaling_factor,
                      "does not respect machine window availability for machine ", machine.get_id())

    if model_consistency:
        print("The schedule is a valid schedule")
    else:
        print("The schedule is an invalid schedule")


def runConnection(optimizer):
    print("Connecting...")
    optimizer.connect()

    model = input("Run model [r(routing)/s(scheduling)/m(mp)/d(data)/c(cp)/p(deploy)/j(job-shop)/n(none)]: ")
    if model == "n":
        pass
    elif model == "r":
        # vrp = createVRPModel(BuildVRP('example'))
        vrp = createMappedVRPModel(BuildVRP('example'))
        optimizer.run_optimizer_synch(vrp)
        solution = vrp.get_solution()
        drivers = vrp.get_model().get_vehicles()
        for driver in drivers:
            print(driver.name)
        for route in solution:
            print("Route: " + str(route.get_route()))
            print("Total distance: " + str(route.get_total_distance()))
    elif model == "d":
        data_tool = createPythonFunctionTool(BuildPythonFunctionTool("fcn_tool"))
        optimizer.run_optimizer_synch(data_tool)
        output = data_tool.get_instance().get_output()
        print(output)
    elif model == "p":
        deployment = DeploymentModel()
        deployment.deploy_model("abc")
        optimizer.run_optimizer_synch(deployment)
    elif model == "c":
        cp = CPModel('cp_model')
        # createCPModel(cp.get_model())
        createSmartGridCPModel(cp.get_model())
        optimizer.run_optimizer_synch(cp)
        solution = cp.get_model().get_solution()
        print(solution)
    elif model == "j":
        js = BuildJobShopScheduler("job_shop")
        createJobShopModel(js)
        # createJobShopModelFromData(js.get_instance())
        optimizer.run_optimizer_synch(js)
        verifyJobShop(js.get_instance())
        js.get_instance().print_solution()
    elif model == "s":
        scheduler = BuildEmployeesScheduler('test')
        createSchedulingModel(scheduler)
        optimizer.run_optimizer_synch(scheduler)
    else:
        pass

    val = input("Disconnect? [Y/N]: ")
    optimizer.disconnect()


def main():
    #vrp = BuildVRP('example')
    #depot = vrp.AddDepot('145+Concord+Rd+Wayland+MA')
    #depot.get_coordinates(API_key="AIzaSyCGOa79k466MIwCERz5_obRhmONuebj5Cs")
    #return

    # cp = CPModel('cp_model')
    # createSmartGridCPModel(cp.get_model())
    # return

    mp = MPModel('mip_example')
    createMPModel(mp)

    data_tool = BuildPythonFunctionTool("fcn_tool")
    createPythonFunctionTool(data_tool)

    js = BuildJobShopScheduler("job_shop")
    createJobShopModel(js)

    print("Create a client...")
    optimizer = ParallelClient('127.0.0.1')
    val = input("Connect to back-end [Y/N]: ")
    if val == 'Y':
        runConnection(optimizer)


if __name__ == '__main__':
    main()
