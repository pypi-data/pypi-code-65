from faker import Faker
from faker.utils import checksums
import random
import string

fake = Faker()

# first, import a similar Provider or use the default one
from faker.providers import BaseProvider

class FormatProvider(BaseProvider):

    #  - Number signs ('#') are replaced with a random digit (0 to 9).
    #  - Percent signs ('%') are replaced with a random non-zero digit (1 to 9).
    #  - Exclamation marks ('!') are replaced with a random digit or an empty string.
    #  - At symbols ('@') are replaced with a random non-zero digit or an empty string.
    #  - Question marks ('?') are replaced with a random character from ``letters``.
    def generate_format_data(self, formats = ('####-###', )):
        return self.bothify(self.random_element(formats))
    #  - ^ symbol represents checksum feild position
    def generate_checksums(self, formats = ('####-###', )):
        digits = self.numerify(self.random_element(formats))
        
        checkstoput = digits.split('^')
        fake_number = ''
        i = 0
        while (i<len(checkstoput)-1):
            checksum = checksums.calculate_luhn(''.join(k for k in checkstoput[i] if k.isdigit()))
            fake_number += '{}{}'.format(checkstoput[i], checksum)
            i += 1
        fake_number += checkstoput[len(checkstoput)-1]
        return fake_number

    def generate_fake(self, formats= ('####-###', ), letters = string.ascii_letters):
        # format_chosen = self.random_element(formats)
        alphas = self.bothify(self.random_element(formats), letters= letters)
        checkstoput = alphas.split('^')
        if(len(checkstoput) > 0):
            fake_number = ''
            i = 0
            tocheck = checkstoput[0]
            while (i<len(checkstoput)-1):
                checksum = checksums.calculate_luhn(''.join(k for k in tocheck if k.isdigit()))
                fake_number += '{}{}'.format(checkstoput[i], checksum)
                tocheck = fake_number
                i += 1
            fake_number += checkstoput[len(checkstoput)-1]
            return fake_number
        else:
            return alphas


fake.add_provider(FormatProvider)

# print(fake.generate_format_data(formats =('8###-####-#',))) # abia routing number
# print(fake.generate_format_data(formats =('##.###.###',))) # argentina national identity number
# print(fake.generate_format_data(formats =('###-###!!!!',))) # australia driver licence number
# print(fake.generate_format_data(formats= ('####???##','??####???','#?###?#?#'))) # australia driver licence number

# # special case. includes /\+= along with digits and letters
# # Austria national identification number
# first = random.choices(['#','/','\\','+'], weights = [12, 4, 4, 2], k = 22) # 22 letters
# second = random.choices(['#','/','\\','+','='], k = 2) # 2 letters
# number_format = ''.join(first) + ''.join(second)
# print(fake.generate_format_data(formats= (number_format,))) # Austria national identification number



# aadhaar_id_formats = (
#         '%##########^',
#     )
# print(fake.generate_checksums(formats= aadhaar_id_formats)) # indian aadhar-card numbers

# print(fake.generate_checksums(formats =('### ### ##^',))) # australia driver licence number
