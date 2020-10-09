import random
import string
def get_random_year(format = 'YYMMDD'):
    part1 = "##"
    part3 = random.choices(['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','25','26','27','28','29','30'])
    part2 = random.choices(['01','02','03','04','05','06','07','08','09','10','11','12'])
    part4 = random.choice(['19,20'])+'##'
    part5 = random.choice(['9,0'])+'##'
    if(format == 'YYYYMMDD'):
        return part4+''.join(part2)+''.join(part3)
    if(format == 'YYYMMDD'):
        return part5+''.join(part2)+''.join(part3)
    elif (format == 'DDMMYY'):
        return ''.join(part3)+''.join(part2)+part1
    else:
        return part1+''.join(part2)+''.join(part3)

def generate_sequential_number(num_size):
    nums = '0123456789'
    seq_number = random.choice(nums[0:len(nums)-num_size])
    num = seq_number
    for n in range(num_size-1):
        num = str(int(num)+1)
        seq_number += num
    return seq_number
class FormatGenerator():
    def generatebyid(id):
        formats = []
        if(id == "abaroutingnumber"):
            for n in range(10):
                formats.append(random.choice('0123678')+'###-####-#')
                formats.append(random.choice('0123678')+'########')
        elif(id == "australiamedicalaccnumber"):
            for n in range(10):
                formats.append(random.choice('23456')+'#######^#!')
        elif(id == "austriassn"):
            for n in range(10):
                formats.append("###^"+ get_random_year('DDMMYY'))
        elif(id=="austrianationalidnumber"): 
            for n in range(10):
                part1 = random.choices(['#','/','\\','+'], weights = [12, 4, 4, 2], k = 22) # 22 letters
                part2 = random.choices(['#','/','\\','+','='], k = 2) # 2 letters
                formats.append(''.join(part1) + ''.join(part2))
        elif(id=="belgiumnationalnumber"):
            for n in range(10):
                formats.append(get_random_year('YYMMDD')+"-"+generate_sequential_number(3)+".^^")
        elif(id=="belgiumtaxidnumber"):
            for n in range(10):
                part1 = "##"
                part2 = random.choice('01')
                part3 = "#"
                part4 = random.choice('0123')
                part5 = "######"
                formats.append(part1+part2+part3+part4+part5)
        elif(id=="brazillegalentitynumber"):
                formats.append("##.###.###\####-^^")
        elif(id=="bulgarianationalidnumber"):
            for n in range(10):
                formats.append(get_random_year('YYMMDD')+'###^')
        elif(id=="canadapassportnumber"):
            for n in range(10):
                formats.append(''.join(random.choices(string.ascii_uppercase,k=2))+'######')
        elif(id=="chinaresidentidcardnumber"):
            for n in range(10):
                formats.append('######'+ get_random_year('YYYYMMDD'+'###^'))
        elif(id=="czechpersonalidnumber"):
            for n in range(10):
                part1=get_random_year('DDMMYY')
                formats.append('#########',part1+'\###','##########',part1+'\###^')
        elif(id=="czechssn"):
            for n in range(10):
                formats.append(get_random_year()+"/###^")
        elif(id=="denmarkpersonalidnumber"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY')+"-###^")
        elif(id=="denmarkssn"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY')+"-###^")
        elif(id=="denmarktaxidnumber"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY')+"-"+ generate_sequential_number(4))
        elif(id=="drugenforcementagencynumber"):
            for n in range(10):
                part1=random.choice('abcdefghjklmnprstux')
                formats.append(part1+"?######^")
        elif(id=="estonianationalidnumber"):
            for n in range(10):
                formats.append(random.choice('123456')+ get_random_year() +'###^')
        elif(id=="estoniataxidnumber"):
            for n in range(10):
                formats.append(random.choice('123456')+ get_random_year() +'###^')
        elif(id=="finlandnationalidnumber"):
            for n in range(10):
                part1 = get_random_year('DDMMYY')
                part2 = random.choice('-+a')
                part3 = "###^"
                formats.append(part1+''.join(part2)+part3)
        elif(id=="finlandssn"):
            for n in range(10):
                part1 = get_random_year('DDMMYY')
                part2 = random.choice('-+A')
                part3 = "###^"
                formats.append(part1+''.join(part2)+part3)
        elif(id=="finlandtaxidnumber"):
            for n in range(10):
                part1 = get_random_year('DDMMYY')
                part2 = random.choice('-+A')
                part3 = "###^"
                formats.append(part1+''.join(part2)+part3)
        elif(id=="francetaxidnumber"):
            for n in range(10):
                formats.append(random.choice(['0','1','2','3'])+"############")
        elif(id=="germanydriverslicensenumber"):
            for n in range(10):
                part1 = random.choice(['#','?'])
                part2 = random.choice(['######','??????'])
                formats.append(part1+"##"+''.join(part2)+"#^")
        elif(id=="germanypassportnumber"):
            for n in range(10):
                part1 = random.choice('#CFGHJK')
                part2 = ''.join(random.choices('#CDEFGHJMNPRTVWXYZ',k=5))
                formats.append(part1+"###"+part2+"#",part1+'########^')
        elif(id=="greecenationalidcard"):
            for n in range(10):
                greek_alphabet = random.choices(['A','B','E','Z','H','I','K','M','N','O','P','T','Y','X'],k=2)
                formats.append('?-######',''.join(greek_alphabet)+"-######")
        elif(id=="hungarynationalidnumber"):
            for n in range(10):
                part1 = get_random_year('YYMMDD')
                formats.append('#'+part1+'###^')
        elif(id=="indonesiaidcardnumber"):
            for n in range(10):
                formats.append('##.####.'+ get_random_year('DDMMYY')+'.####','######'+ get_random_year('DDMMYY')+'####')
        elif(id=="irelandnationalidnumber"):
            for n in range(10):
                formats.append('#######^ ','#######^W','#######^ ','#######^'+random.choice(string.ascii_uppercase))
        elif(id=="irelandpersonalpublicservicenumber"):
            for n in range(10):
                formats.append('??#######','?#######','#######??','#######?','#######^'+''.join(random.choice('AH')))
        elif(id=="italydriverslicensenumber"):
            for n in range(10):
                formats.append('?A'+''.join(random.choices('?#_',k=7))+'?','?V'+''.join(random.choices('?#_',k=7))+'?')
        elif(id=="italynationalidnumber"):
            for n in range(10):
                formats.append('########'+random.choice('AEHLMPRT')+'######^')
        elif(id=="italytaxidnumber"):
            for n in range(10):
                formats.append('########'+random.choice('AEHLMPRT')+'######^')
        elif(id=="japanssn"):
            for n in range(10):
                formats.append('#######' + str(random.randint(1, 99999)))
        elif(id=="lativianationalidnumber"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY')+'-#####')
        elif(id=="latviataxidnumber"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY')+'-'+ random.choice('012')+'###^')
        elif(id=="lithuanianationalidnumber"):
            for n in range(10):
                formats.append('#'+get_random_year('YYMMDD')+'-###^')
        elif(id=="lithuaniapassportnumber"):
            for n in range(10):
                formats.append(''.join(random.choices('#?', k=8)))
        elif(id=="luxemburgnationalidnumber"):
            for n in range(10):
                formats.append('#'+get_random_year('YYMMDD')+'-###^')
        elif(id=="luxemburgpassportnumber"):
            for n in range(10):
                formats.append(''.join(random.choices('#?', k=8)))
        elif(id=="malaysiaidcardnumber"):
            for n in range(10):
                formats.append(get_random_year()+'-??-###'+''.join(random.choices('01')))
                formats.append(get_random_year()+'??###'+''.join(random.choices('01')))
        elif(id=="maltanationalidnumber"):
            for n in range(10):
                formats.append('#######'+ ''.join(random.choices(string.ascii_uppercase)))
        elif(id=="netherlandspassportnumber"):
            for n in range(10):
                formats.append(''.join(random.choices('#?', k=9)))
        elif(id=="norwayidnumber"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY')+'###^^')
        elif(id=="singaporenationalregistrationidcard"):
            for n in range(10):
                formats.append(random.choice('FGST')+'#######^')
        elif(id=="slovenianationalid"):
            for n in range(10):
                formats.append(get_random_year('DDMMYY') + '######^')
        elif(id=="sloveniapassportnumber"):
            for n in range(10):
                formats.append('P'+ random.choice(string.ascii_uppercase)+'#######')
        elif(id=="southafricaidnumber"):
            for n in range(10):
                formats.append(get_random_year('YYMMDD')+'#####'+random.choice('89')+'^')
        elif(id=="southkorearesidentregistrationnumber"):
            for n in range(10):
                formats.append(get_random_year('YYMMDD')+'-######^')
        elif(id=="spainpassportnumber"):
            for n in range(10):
                formats.append(''.join(random.choice(['##','??']))+''.join(random.choice('?#')+'######'),''.join(random.choice(['##','??']))+''.join(random.choice('?#'))+'######')
        elif(id=="spaintaxidnumber"):
            for n in range(10):
                formats.append('########'+ ''.join(random.choices(string.ascii_uppercase)),''.join(random.choices('LKXYZM'))+'#######'+ ''.join(random.choices(string.ascii_uppercase)))
        elif(id=="swedennationalid"):
            for n in range(10):
                formats.append(str(random.randint(10,9999))+get_random_year('YYMMDD')+random.choice('-+')+'###^')
        elif(id=="swedenssn"):
            for n in range(10):
                formats.append(get_random_year('YYYYMMDD')+'###^')
        elif(id=="swedentaxidnumber"):
            for n in range(10):
                formats.append(get_random_year('YYMMDD')+random.choice('+-/')+'###^')
        elif(id=="thaipopulationidcode"):
            for n in range(10):
                formats.append(random.choice('12345678')+'###########^')
        elif(id=="ukdriverslicensenumber"):
            for n in range(10):
                formats.append('?????#'+get_random_year('MMDDY')+'??####^','9#'+get_random_year('MMDDY')+'9####^')
        elif(id=="ukelectoralrollnumber"):
            for n in range(10):
                formats.append('??'+str(random.randint(0,9999)))
        elif(id=="uknationalhealthservicenumber"):
            for n in range(10):
                formats.append(''.join(random.choices('#',k=random.randint(3,10)))+' ### ###^')
        elif(id=="uknationalinsurancenumber"):
            for n in range(10):
                l = random.choice('ABCD')
                formats.append('??######'+l,'## ## ## ## '+l,'##-##-##-##-'+l,'## ## ## ## '+l)
        elif(id=="usbankaccnumber"):
            for n in range(10):
                formats.append(''.join(random.choices('#',k=random.randint(8,17))))
        return formats
        