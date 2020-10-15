# import libs
from wasabi import Printer

# start the mommy class
class mommy():

    # define class structure
    def __init__(self, name=None):

        # object slots
        self.name = name

        # check if name was given
        if self.name is None:

            # set name to default
            self.name = "Mommy"

        # initialize Printer
        msg = Printer()

        # print heading
        msg.divider(str("Welcome " + self.name))

        # create info section
        info_section = """

Congrats to becoming a mum. Mums are amazing and it is the greatest miracle,
that you can great life. I hope you are proud of yourself, cause you did the
single most beautiful thing in the world, you gave life.

To start the advice section, you can just run the advice() method and I will 
guide you, hoping that you can please your little wonder.

Cheers and keep it up.

        """

        # print info
        print (info_section)

    # define advice function
    def get_advice(self):

        # initialize Printer
        msg = Printer()

        # print info message
        msg.info("Okay, " + self.name + " keep calm, I will guide you")

        # check the sex of the baby
        sex = input("Are you searching for adivce on a boy or a girl? ")

        # check if fed properly
        fed = input(str("Was your " + sex + 
                        " fed properly in the last 1.5 hours? (yes/no) "))

        # evaluate if baby is maybe hungry
        if fed=="no":
            
            # suggest trying to feed the baby
            msg.warn("Maybe your " + sex + " is hungry, try some nice food!")

            # break out of function
            return None

        # check if slept properly
        slept = input(str("Has your " + sex +
                          " slept properly in the last 4 hours? (yes/no) "))

        # evaluate if baby is maybe tired
        if slept=="no":

            # suggest trying to put the baby to sleep
            msg.warn("Maybe your " + sex + " is tired and wants to sleep!")

            # check if baby has problems falling asleep
            sleep_issues = input(str("Has your " + sex +
                                     " problems falling asleep? (yes/no) "))
                
            # check if baby needs some extra cuddling
            if sleep_issues=="yes":

                # print info
                msg.info("Maybe some extra cuddling and singing might help")

                # break out of function
                return None

            # break out of function
            return None    

        


