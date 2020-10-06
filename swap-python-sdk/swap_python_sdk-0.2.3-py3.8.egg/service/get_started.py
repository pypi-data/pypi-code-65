from os import getcwd
from swap.service.developer_helper import check_latest_version_of_sdk
from swap.service.generate_config import ConfigGenerator


class GetStarted:
    def generate_config(self):
        print('Now that dependencies have been installed, a new configuration will be generated for your service')

        config_output_path = getcwd() + '/config.py'

        config_generator = ConfigGenerator(config_output_path=config_output_path)

        config_generator.write()

    def continue_get_started(self, production):
        if production == True:
            print('Preparing service in production environment...')
        check_latest_version_of_sdk()
        self.generate_config()
        print("You are now ready to code your service using the file 'service.py'")
        print("When you're ready to run your service, use the following command:\npipenv run python service.py")
