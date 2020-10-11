# tello base library extention 
# for Tello EDU KIT

import serial
import time
import threading
import serial.tools.list_ports

module = ''
# functions for modules

def get_temp():
    '''Returns the air temperature'''
    if module == 'sensor':
        return info_sensor['temp']
    return 0

def get_pressure():
    '''Returns the atmosphere pressure'''
    if module == 'sensor':
        return info_sensor['pressure']
    return 0

def get_humidity():
    '''Returns the air humidity'''
    if module == 'sensor':
        return info_sensor['humidity']
    return 0

def get_TVOC():
    '''Returns the air quality index'''
    if module == 'sensor':
        return info_sensor['TVOC']
    return 0

def get_CO2():
    '''Returns the level of CO2 in the air'''
    if module == 'sensor':
        return info_sensor['CO2']
    return 0

def get_lightness():
    '''Returns the brightness level'''
    if module == 'sensor':
        return info_sensor['light']
    if module == 'distance':
        return info_distance['light']
    return 0
    
def get_forward_dist():
    '''Returns the front side distance'''
    if module == 'distance':
        return info_distance['forward_dist']
    return 0

def get_left_dist():
    '''Returns the left side distance'''
    if module == 'distance':
        return info_distance['left_dist']
    return 0

def get_right_dist():
    '''Returns the right side distance'''
    if module == 'distance':
        return info_distance['right_dist']
    return 0

def get_back_dist():
    '''Returns the rear side distance'''
    if module == 'distance':
        return info_distance['back_dist']
    return 0

# DIOD1
def L1_red():
    '''Turns the lamp 1 red light on'''
    L1_off()
    ser.write(bytes('L1=1', 'utf-8'))
    
def L1_green():
    '''Turns the lamp 1 green light on'''
    L1_off()
    ser.write(bytes('L2=1', 'utf-8'))
    
def L1_yellow():
    '''Turns the lamp 1 yellow (red+green) light on'''
    ser.write(bytes('L1=1', 'utf-8'))
    ser.write(bytes('L2=1', 'utf-8'))
    
def L1_off():
    '''Turns the lamp 1 light off'''
    ser.write(bytes('L1=0', 'utf-8'))
    ser.write(bytes('L2=0', 'utf-8'))
    
# DIOD2
def L2_red():
    '''Turns the lamp 2 red light on'''
    L2_off()
    ser.write(bytes('L4=1', 'utf-8'))
    
def L2_green():
    '''Turns the lamp 2 green light on'''
    L2_off()
    ser.write(bytes('L3=1', 'utf-8'))
    
def L2_yellow():
    '''Turns the lamp 2 yellow (red+green) light on'''
    ser.write(bytes('L3=1', 'utf-8'))
    ser.write(bytes('L4=1', 'utf-8'))
    
def L2_off():
    '''Turns the lamp 2 light off'''
    ser.write(bytes('L3=0', 'utf-8'))
    ser.write(bytes('L4=0', 'utf-8'))    
    
# DIOD3
def L3_red():
    '''Turns the lamp 3 red light on'''
    L3_off()
    ser.write(bytes('L6=1', 'utf-8'))
    
def L3_green():
    '''Turns the lamp 3 green light on'''
    L3_off()
    ser.write(bytes('L5=1', 'utf-8'))
    
def L3_yellow():
    '''Turns the lamp 3 yellow (red+green) light on'''
    ser.write(bytes('L5=1', 'utf-8'))
    ser.write(bytes('L6=1', 'utf-8'))
    
def L3_off():
    '''Turns the lamp 3 light off'''
    ser.write(bytes('L5=0', 'utf-8'))
    ser.write(bytes('L6=0', 'utf-8'))    

# DIOD4
def L4_red():
    '''Turns the lamp 4 red light on'''
    L4_off()
    ser.write(bytes('L7=1', 'utf-8'))

def L4_green():
    '''Turns the lamp 4 green light on'''
    L4_off()
    ser.write(bytes('L8=1', 'utf-8'))

def L4_yellow():
    '''Turns the lamp 4 yellow (red+green) light on'''
    ser.write(bytes('L7=1', 'utf-8'))
    ser.write(bytes('L8=1', 'utf-8'))
    
def L4_off():
    '''Turns the lamp 4 light off'''
    ser.write(bytes('L7=0', 'utf-8'))
    ser.write(bytes('L8=0', 'utf-8')) 

# DIOD5
def L5_red():
    '''Turns the lamp 5 red light on'''
    L5_off()
    ser.write(bytes('L9=1', 'utf-8'))

def L5_green():
    '''Turns the lamp 5 green light on'''
    L5_off()
    ser.write(bytes('L0=1', 'utf-8'))

def L5_yellow():
    '''Turns the lamp 5 yellow (red+green) light on'''
    ser.write(bytes('L9=1', 'utf-8'))
    ser.write(bytes('L0=1', 'utf-8'))
    
def L5_off():
    '''Turns the lamp 5 light off'''
    ser.write(bytes('L9=0', 'utf-8'))
    ser.write(bytes('L0=0', 'utf-8')) 

# laser pointer
def laser_on():
    '''Turns the laser pointer on'''
    ser.write(bytes('LL=1', 'utf-8'))

def laser_off():
    '''Turns the laser pointer off'''
    ser.write(bytes('LL=0', 'utf-8'))

# beeper    
def beep_on():
    '''Turns the beeper on'''
    ser.write(bytes('BP=1', 'utf-8'))

def beep_off():
    '''Turns the laser pointer off'''
    ser.write(bytes('BP=0', 'utf-8'))
    
def reset_all():
    '''Turns all the feedback off'''
    L1_off()
    L2_off()
    L3_off()
    L4_off()
    L5_off()    
    laser_off()
    beep_off()        

def flash_all():
    '''Turns all the feedback on'''
    L1_red()
    L2_yellow()
    L3_red()
    L4_green()
    L5_green()    
    laser_on()
    beep_on() 

info_distance = {'count': 0,
                 'forward_dist': 0,
                 'right_dist': 0,
                 'back_dist': 0,
                 'left_dist': 0,
                 'light': 0}

info_sensor = {'count': 0,
               'temp': 0,
               'pressure': 0,
               'humidity': 0,
               'TVOC': 0,
               'CO2': 0,
               'light': 0}
# список портов
ports = list(serial.tools.list_ports.comports())
for p in ports: 
    if "Prolif" in str(p) or "Prolif" in p.manufacturer or "SBRICKS" in \
            p.manufacturer or 'FTDI' in p.manufacturer:
        port_name = str(p)[:5].strip()
        break

else:
    print("Передатчик не найден.")
    exit()        
# определение порта
serial_port = p.device
#ser = serial.Serial(port_name)
ser = serial.Serial(serial_port)
# print(port_name)
ser.baudrate = 115200
e = 0
while e == 0:
# чтение и парсинг строки данных
    line = str(ser.readline())[4:-3].split()
    line_count = len(line) 
    if line_count == 6:
        module = 'distance'
    elif line_count == 7:
        module = 'sensor'
    elif line_count == 1:
        module = 'feedback'
    else:
        module = None
    if module == 'sensor':  
        number_of_data_string = line[0][2:]
        temperature = 'Температура, \u00b0С: \t\t' + line[1][2:]
        pressure = 'Атм. давление, мм рт.ст.: \t' + line[2][2:]
        humidity = 'Отн. влажность, %: \t\t' + line[3][2:]
        quality_index = 'Индекс качества воздуха: \t' + line[4][5:]
        co2_index = 'Индекс уровня CO2: \t\t' + line[5][4:]
        lightness = 'Уровень освещенности: \t\t' + line[6][6:]
        info_sensor['count'] = int(line[0][2:])
        info_sensor['temp'] = float(line[1][2:])
        info_sensor['pressure'] = float(line[2][2:])
        info_sensor['humidity'] = float(line[3][2:])
        info_sensor['TVOC'] = int(line[4][5:])
        info_sensor['CO2'] = int(line[5][4:])
        info_sensor['light'] = int(line[6][6:])        
        # вывод   
        print('Подключен датчик ЭКОЛОГИЯ. Тест:')
        #print(number_of_data_string)
        print(temperature)
        print(pressure)
        print(humidity)
        print(quality_index)
        print(co2_index)
        print(lightness)
    elif module == 'distance': 
        print('Подключен датчик ЛАБИРИНТ. Тест:')
        count = str(line[0])
        forward = 'Дистанция спереди: \t' + str(line[1][6:]) 
        right = 'Дистанция справа: \t' + str(line[2][6:]) 
        back = 'Дистанция сзади: \t' + str(line[3][6:]) 
        left = 'Дистанция слева: \t' + str(line[4][6:]) 
        lightness = 'Уровень освещенности: \t' + str(line[5][6:]) 
        info_distance['count'] = int(line[0][2:])
        info_distance['forward_dist'] = int(line[1][6:])
        info_distance['right_dist'] = int(line[2][6:])
        info_distance['back_dist'] = int(line[3][6:])
        info_distance['left_dist'] = int(line[4][6:])
        info_distance['light'] = int(line[5][6:])        
        print(forward)
        print(right)
        print(back)
        print(left)
        print(lightness)
    elif module == 'feedback': 
        print('Подключен датчик ОБРАТНАЯ СВЯЗЬ.')
        '''
        flash_all()
        time.sleep(1)
        
        '''
    else:
        print('Датчик не найден.')
    e = 1
    