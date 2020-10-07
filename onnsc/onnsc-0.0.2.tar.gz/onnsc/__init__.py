"""Convenience Python module for Trend Micro Smart Check
## Example

    from onnsc import Sc

    def main():
        username = 'administrator'
        password = 'password'
        base_url = 'example.com'

        # change password
        sc.change_password(original_password=password, new_password='ChangeMeAgain')

        # create a new user & give them "user" permissions
        role_id_map = sc.get_role_id_map()
        user_role_id = role_id_map['user']
        sc.create_user('lab10', 'password', user_role_id)

    if __name__ == '__main__':
        main()

## Installation

    pip3 install onnsc

## Contact
* Code: [onnsc](https://github.com/OzNetNerd/onnsc)
* Blog: [oznetnerd.com](https://oznetnerd.com)
* Email: [will@oznetnerd.com](mailto:will@oznetnerd.com)
"""

from .sc import Sc