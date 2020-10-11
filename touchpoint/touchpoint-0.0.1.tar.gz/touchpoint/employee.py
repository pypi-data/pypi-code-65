# touchpoint/employee.py

class Employee():
    def __init__(self, employee_id, first_name=None, last_name=None, emp_id=None):
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.emp_id = emp_id

    def info(self):
        return {'employee_id': self.employee_id,
                'emp_id': self.emp_id,
                'first_name': self.first_name,
                'last_name': self.last_name}
