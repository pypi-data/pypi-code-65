from time import time
from time import localtime
from time import strftime
from functools import partial
from functools import wraps
from inspect import getcallargs
from math import log

################################### 全局常量 ################################
nowTime = strftime("%Y-%m-%d %H:%M:%S",localtime(time()))#获取当前时间
#c文件的固定部分
autoLibC = """\
/* %s */
#include <stm32f10x.h>
#include "AutoLib.h"

void delay(float sec) {
	SysTick->LOAD = (int)(sec*9000000);
	SysTick->VAL = 0;
	SysTick->CTRL = 1;
	while(!READ_BIT(SysTick->CTRL,SysTick_CTRL_COUNTFLAG));
	SysTick->CTRL = 0;
}

void autoLibInit(void) { //autoLib初始化
	/*外部高速时钟使能*/
	SET_BIT(RCC->CR, RCC_CR_HSEON);
	/*等待外部时钟就绪*/
	while (READ_BIT(RCC->CR, RCC_CR_HSERDY) == 0);
	/*HCLK 2分频*/
	RCC->CFGR = RCC_CFGR_PPRE1_DIV2;
	/*设置PLL9倍频输出*/
	SET_BIT(RCC->CFGR, 0x1C0000);
	/*HSE作为PLL时钟源*/
	SET_BIT(RCC->CFGR, RCC_CFGR_PLLSRC);
	/*FLASH 2个延时周期*/
	FLASH->ACR|=0x32;
	/*PLL使能*/
	SET_BIT(RCC->CR, RCC_CR_PLLON);
	/*等待PLL锁定*/
	while(READ_BIT(RCC->CR, RCC_CR_PLLRDY) == 0);
	/*PLL作为系统时钟*/
	SET_BIT(RCC->CFGR, RCC_CFGR_SW_PLL);
	/*等待PLL作为系统时钟设置就绪*/
	while(READ_BIT(RCC->CFGR, RCC_CFGR_SWS) != 0x08);

"""%nowTime
#头文件的固定部分
autoLibH = """\
/* %s */
#ifndef AUTOLIB_H_
#define AUTOLIB_H_

#include <stm32f10x.h>

/*位带操作定义*/
#define BITBAND(addr, bitnum) ((addr & 0xF0000000)+0x2000000+((addr &0xFFFFF)<<5)+(bitnum<<2))
#define MEM_ADDR(addr) *((volatile unsigned long  *)(addr))
#define BIT_ADDR(addr, bitnum) MEM_ADDR(BITBAND(addr, bitnum))

void autoLibInit(void);
void delay(float sec);
"""%nowTime


############################ 异常处理 ################################
class AutoLibException(Exception):
    pass


def error(info):
    raise AutoLibException("[错误]"+info)


def check(**ckwargs):
    "检查关键字参数是否合法,并初步处理"
    def decorator(f):
        @wraps(f)
        def wrapped(*args,**kwargs):
            callargs = getcallargs(f,*args,**kwargs)
            for key,checker in ckwargs.items():
                #所有被检查的关键字参数转换为大写和数字
                if key.endswith('s'):
                    callargs[key] = tuple(int(i) for i in callargs[key].split())
                elif type(callargs[key])==str:
                    callargs[key]=callargs[key].upper()
                    if callargs[key].isdigit():
                        try:
                            callargs[key] = int(callargs[key])
                        except ValueError:
                            callargs[key] = float(callargs[key])
                if not checker(callargs[key]):
                    error("参数错误：%s不能为%s"%(key,callargs[key]))
            return f(**callargs)
        return wrapped
    return decorator


def inRange(num,end,start=0):
    return start<=num<=end

################################# 类定义 ##################################
class Function(object):
    """
    AutoLib所有功能需要实现的接口
    """
    def getInit(self):
        "获取实现此功能之前需要执行的代码"
        return self.init
    def getRCC(self):
        "获取实现此功能需要开启时钟的外设"
        return self.rcc
    def getIO(self):
        "获取实现此功能需要占用的io口"
        return self.io
    def getHandle(self):
        "获取控制此功能用的函数体代码"
        return self.handle
    def getHeader(self):
        "获取控制此功能用的函数声明"
        return self.header


RCC = { #开启外设时钟使用的代码
    "GPIOA":"/*使能GPIOA时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPAEN);",
    "GPIOB":"/*使能GPIOB时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPBEN);",
    "GPIOC":"/*使能GPIOC时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPCEN);",
    "GPIOD":"/*使能GPIOD时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPDEN);",
    "GPIOE":"/*使能GPIOE时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPEEN);",
    "GPIOF":"/*使能GPIOF时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPFEN);",
    "GPIOG":"/*使能GPIOG时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_IOPGEN);",
    "AFIO":"/*使能AFIO时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_AFIOEN);",
    "TIM1":"/*使能TIM1时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM1EN);",
    "TIM2":"/*使能TIM2时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM2EN);",
    "TIM3":"/*使能TIM3时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM3EN);",
    "TIM4":"/*使能TIM4时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM4EN);",
    "TIM5":"/*使能TIM5时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM5EN);",
    "TIM6":"/*使能TIM6时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM6EN);",
    "TIM7":"/*使能TIM7时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM7EN);",
    "TIM8":"/*使能TIM8时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM8EN);",
    "TIM9":"/*使能TIM9时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM9EN);",
    "TIM10":"/*使能TIM10时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM10EN);",
    "TIM11":"/*使能TIM11时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM11EN);",
    "TIM12":"/*使能TIM12时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM12EN);",
    "TIM13":"/*使能TIM13时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM13EN);",
    "TIM14":"/*使能TIM14时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_TIM14EN);",
    "TIM15":"/*使能TIM15时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM15EN);",
    "TIM16":"/*使能TIM16时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM16EN);",
    "TIM17":"/*使能TIM17时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_TIM17EN);",
    "USART1":"/*使能USART1时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_USART1EN);",
    "USART2":"/*使能USART2时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_USART2EN);",
    "USART3":"/*使能USART3时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_USART3EN);",
    "USART4":"/*使能USART4时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_USART4EN);",
    "USART5":"/*使能USART5时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_USART5EN);",
    "DMA1":"/*使能DMA1时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_DMA1EN);",
    "DMA2":"/*使能DMA2时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_DMA2EN);",
    "ADC1":"/*使能ADC1时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_ADC1EN);",
    "ADC2":"/*使能ADC2时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_ADC2EN);",
    "ADC3":"/*使能ADC3时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_ADC3EN);",
    "DAC":"/*使能DAC时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_DACEN);",
    "I2C1":"/*使能I2C1时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_I2C1EN);",
    "I2C2":"/*使能I2C2时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_I2C2EN);",
    "SPI1":"/*使能SPI1时钟*/\n\tSET_BIT(RCC->APB2ENR,RCC_APB2ENR_SPI1EN);",
    "SPI2":"/*使能SPI2时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_SPI2EN);",
    "SPI3":"/*使能SPI3时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_SPI3EN);",
    "CAN1":"/*使能CAN1时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_CAN1EN);",
    "CAN2":"/*使能CAN2时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_CAN2EN);",
    "SRAM":"/*使能SRAM时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_SRAMEN);",
    "FLITF":"/*使能FLITF时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_FLITFEN);",
    "CRC":"/*使能CRC时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_CRCEN);",
    "FSMC":"/*使能FSMC时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_FSMCEN);",
    "SDIO":"/*使能SDIO时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_SDIOEN);",
    "FSMC":"/*使能FSMC时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_FSMCEN);",
    "OTGFS":"/*使能OTGFS时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_OTGFSEN);",
    "ETHMAC":"/*使能ETHMAC时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_ETHMACEN);",
    "ETHMACTX":"/*使能ETHMACTX时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_ETHMACTXEN);",
    "ETHMACRX":"/*使能ETHMACRX时钟*/\n\tSET_BIT(RCC->AHBENR,RCC_AHBENR_ETHMACRXEN);",
    "WWDG":"/*使能WWDG时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_WWDGEN);",
    "BKP":"/*使能BKP时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_BKPEN);",
    "PWR":"/*使能PWR时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_PWREN);",
    "USB":"/*使能USB时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_USBEN);",
    "CEC":"/*使能CEC时钟*/\n\tSET_BIT(RCC->APB1ENR,RCC_APB1ENR_CECEN);"
}


def parsePort(port):
    "把io口名称拆成两部分：A10->A,10 返回str,int"
    return (port[0],int(port[1:]))

def portChecker(port):
    port,pin = parsePort(port)
    return port in "ABCDEF" and inRange(pin,15)

def ioSpeedChecker(speed):
    return speed in ("HIGH","MID","LOW")

def ioModeChecker(mode):
    return mode in ("AIN","IN","IPD","IPU","OD","PP","AFOD","AFPP","AFIN")


class IO(Function):
    """
    io端口抽象
    speed=HIGH 50MHz
        MID 10MHz
        LOW 2MHz
    mode=AIN 模拟输入
        IN 浮空输入
        IPD 上拉输入
        IPU 下拉输入
        OD 开漏输出
        PP 推挽输出
        AFOD 复用开漏输出
        AFPP 复用推挽输出
        AFIN 复用输入
    """
    @check(port=portChecker,speed=ioSpeedChecker,mode=ioModeChecker)
    def __init__(self,port,speed="HIGH",mode="PP",name=None):
        MODE = { #映射模式到模式代码
            "AIN":0,
            "IN":4,
            "IPD":8,
            "IPU":8,
            "OD":4,
            "PP":0,
            "AFOD":12,
            "AFPP":8,
            "AFIN":8
            }
        MODE_NAME = {
            "AIN": "模拟输入",
            "IN": "浮空输入",
            "IPD": "上拉输入",
            "IPU": "下拉输入",
            "OD": "开漏输出",
            "PP": "推挽输出",
            "AFOD": "复用开漏输出",
            "AFPP": "复用推挽输出",
            "AFIN":"复用输入"
            }
        SPEED = { #映射速度到速度代码
            "HIGH":3,
            "MID":1,
            "LOW":2
            }
        SPEED_NAME = {
            "HIGH":"50MHz",
            "MID":"10MHz",
            "LOW":"2MHz"
            }

        if not name:
            self.name = port
        else:
            self.name = name
        self.port,self.pin = parsePort(port)
        self.rcc = ["GPIO%s"%self.port] #开启时钟
        cr = "L" if self.pin<8 else "H" #判断配置CRL还是CRH
        bit = (self.pin%8)*4 #此位在CR寄存器中的位置
        if mode in ("AIN","IN","IPD","IPU","AFIN"): #输入模式
            self.isInput = True
            code = MODE[mode] #输入模式没有速度
        else:
            self.isInput = False
            code = MODE[mode] + SPEED[speed]
        self.init = list()
        self.init.append("/*配置%s(%s)模式为%s,%s*/"%(self.name,port,MODE_NAME[mode],SPEED_NAME[speed]))
        #清理CR寄存器对应的位
        self.init.append("GPIO%s->CR%s &= 0x%08X;"%(self.port,cr,0xFFFFFFFF^(0xF<<bit)))
        #写入CR寄存器
        self.init.append("GPIO%s->CR%s |= 0x%08X;"%(self.port,cr,code<<bit))
        #上拉或下拉模式下需要额外写入ODR寄存器
        if mode == "IPD":
            self.init.append("CLEAR_BIT(GPIO%s->ODR,GPIO_ODR_ODR%s);"%(self.port,self.pin))
        elif mode == "IPU":
            self.init.append("SET_BIT(GPIO%s->ODR,GPIO_ODR_ODR%s);"%(self.port,self.pin))

    def getIO(self):
        return [self]

    def getHandle(self):
        return list()

    def getHeader(self):
        #获取位带地址，IDR+8，ODR+12
        header = self.getInit()
        header.append(self.getOutput())
        return header

    def getInit(self):
        return list()

    def __eq__(self,other):
        return self.port==other.port and self.pin==other.pin

    def getOutput(self,name=None):
        return "#define %s BIT_ADDR(GPIO%s_BASE+12,%s)"%(name if name else self.name,self.port,self.pin)
    def getInput(self,name=None):
        return "#define %s BIT_ADDR(GPIO%s_BASE+8,%s)"%(name if name else self.name,self.port,self.pin)
    def changeMode(self,name,mode):
        init = IO(port=self.port+str(self.pin),mode=mode).init[1:]
        return "#define %s %s%s"%(name if name else self.name,init[0],init[1])


TIM_CHANNEL = { #记录定时器io口
    "TIM2":(("A0","A1","A2","A3"),
        ("A15","B3","A2","A3"),
        ("A0","A1","B10","B11"),
        ("A15","B3","B10","B11")),
    "TIM3":(("A6","A7","B0","B1"),
        None,
        ("B4","B5","B0","B1"),
        ("C6","C7","C8","C9")),
    "TIM4":(("B6","B7","B8","B9"),
        ("D12","D13","D14","D15")),
    "TIM5":(("A0","A1","A2","A3"),)
    }


def timChecker(tim):
    return tim in TIM_CHANNEL

def timDrctChecker(drct):
    return drct in ("CENTER1","CENTER2","CENTER3","UP","DOWN")

class TIM(Function):
    """
    **通用**定时器功能
    tim 定时器名称 TIM2,TIM3,TIM4,TIM5
    arr 自动重装载值 0~0xFFFF
    psc 预分频系数 0~0xFFFF
    drct 计数方向，默认向上：
            CENTER1
            CENTER2
            CENTER3
            UP
            DOWN
    """
    in65535 = partial(inRange,end=65535)

    @check(tim=timChecker,arr=in65535,psc=in65535,drct=timDrctChecker)
    def __init__(self,name,tim,arr=65535,psc=1,drct="UP"):
        self.name = name
        self.tim = tim.upper()
        self.arr = int(arr)
        self.psc = int(psc)
        self.drct = drct.upper()

        self.init = list()
        self.init.append("/*设定%s的自动重装载值*/"%self.tim)
        self.init.append("%s->ARR = %s;"%(self.tim,self.arr))
        self.init.append("/*设定%s的预分频系数*/"%self.tim)
        self.init.append("%s->PSC = %s;"%(self.tim,self.psc))
        #设定计数方向
        if self.drct != "UP":#向上计数不用设定
            if self.drct.find("CENTER")+1:#中央计数设定
                mode = int(self.drct[-1])
                self.init.append("%s_BIT(%s->CR1,TIM_CR1_CMS_0);"%("CLEAR" if mode==2 else "SET",self.tim))
                self.init.append("%s_BIT(%s->CR1,TIM_CR1_CMS_1);"%("CLEAR" if mode==1 else "SET",self.tim))
            else:#向下计数
                self.init.append("SET_BIT(%s->CR1,TIM_CR1_DIR);"%self.tim)
        self.rcc = [self.tim]
        self.io = list()
        self.handle = list()
        self.header = list()


    def getInit(self):#最后再使能计时器
        self.init.append("/*使能%s*/"%self.tim)
        self.init.append("SET_BIT(%s->CR1,TIM_CR1_CEN);"%self.tim)
        return self.init


def timChsChecker(chs):
    if len(chs)==len(set(chs)):
        return all(map(partial(inRange,start=1,end=4),chs))
    return False

def pwmModeChecker(modes):
    return all(map(partial(inRange,start=1,end=2),modes))

class PWM(TIM):
    """
    PWM输出功能，基于计时器功能
    ch 通道，用空白符分隔，1~4
    mode PWM模式，用空白符分隔，1或2
    remap 重映射选择
        0 没有重映射
        1,2 部分重映射 **TIM3部分重映射只用1**
        3 完全重映射
    """
    @check(chs=timChsChecker,modes=pwmModeChecker,remap=partial(inRange,end=3))
    def __init__(self,tim,chs,name=None,arr=65535,psc=1,drct="UP",modes="1 1 1 1",remap=0):
        if not name:
            self.name = "PWM_tim%s"%(tim)
        else:
            self.name = name
        super().__init__(name=name,tim=tim,arr=arr,psc=psc,drct=drct)#初始化定时器
        self.ch = chs
        self.mode = modes
        self.remap = int(remap)
        #初始化io口为复用推挽输出
        self.io = [IO(port=TIM_CHANNEL[self.tim][self.remap][i-1],mode="AFPP",name="%s_ch%s"%(self.name,i)) for i in self.ch]
        self.rcc.append("AFIO")#使能AFIO
        #配置重映射
        if self.remap:
            if self.remap == 3:
                self.init.append("/*配置%s完全重映射*/"%self.tim)
                self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_%s_REMAP_FULLREMAP);"%self.tim)
            elif self.remap == 2:#只有TIM2有部分重映射2
                self.init.append("/*配置TIM2部分重映射2*/")
                self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_TIM2_REMAP_PARTIALREMAP2);")
            else:
                if self.tim == "TIM2":
                    self.init.append("/*配置TIM2部分重映射1*/")
                    self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_TIM2_REMAP_PARTIALREMAP1);")
                elif self.tim == "TIM3":
                    self.init.append("/*配置TIM3部分重映射*/")
                    self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_TIM3_REMAP_PARTIALREMAP);")
                elif self.tim == "TIM4":
                    self.init.append("/*配置TIM4重映射*/")
                    self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_TIM4_REMAP);")
        #配置各通道
        for ch,mode in zip(self.ch,self.mode):
            ccmr = 1 if ch<3 else 2#决定配置CCMR1还是CCMR2
            self.init.append("/*设置%sch%s的模式为PWM%s*/"%(self.tim,ch,mode))
            self.init.append("SET_BIT(%s->CCMR%s,TIM_CCMR%s_OC%sM);"%(self.tim,ccmr,ccmr,ch))
            if mode == 1:#如果是pwm1模式，把TIM_CCMRx_OCxM寄存器最低位置零
                self.init.append("CLEAR_BIT(%s->CCMR%s,TIM_CCMR%s_OC%sM_0);"%(self.tim,ccmr,ccmr,ch))
            self.init.append("/*使能%sch%s的预装载器*/"%(self.tim,ch))
            self.init.append("SET_BIT(%s->CCMR%s,TIM_CCMR%s_OC%sPE);"%(self.tim,ccmr,ccmr,ch))
            self.init.append("/*配置%sch%s为输出*/"%(self.tim,ch))
            self.init.append("SET_BIT(%s->CCER,TIM_CCER_CC%sE);"%(self.tim,ch))
            self.header.append("#define %s %s->CCR%s"%(TIM_CHANNEL[self.tim][self.remap][ch-1],self.tim,ch))
        self.init.append("/*允许%s自动重装载*/"%self.tim)
        self.init.append("SET_BIT(%s->CR1,TIM_CR1_ARPE);"%self.tim)


USART_PORT = { #USART端口数据(TX,RX,CK,CTS,RTS) 资料不全
        "USART1":(("A9","A10"),
            ("B6","B7")),
        "USART2":(("A2","A3","A4","A0","A1"),
            ("D5","D6","D7","D3","D4")),
        "USART3":(("B10","B11","B12","B13","B14"),
            ("C10","C11","C12","B13","B14"),
            ("D8","D9","D10","D11","D12")),
        "USART4":(("C10","C11")),
        "USART5":(("C12","D2"))
        }


def usartChecker(usart):
    return usart in USART_PORT

def usartVerifyChecker(verify):
    return verify in ("NONE","ODD","EVEN")

def usartStopChecker(stop):
    return stop in (0.5,1,1.5,2)

class USART(Function):
    """
    通用同步异步收发器：串口
    **波特率以PCLK2为72MHz计算**
    usart 串口号：USART1~5
    baud 波特率
    word 字长: 8~9
    verify 校验:
        NONE 无
        ODD 奇校验
        EVEN 偶校验
    irq 中断：0~1 开启PEIE(奇偶校验错误)和TXEIE(接受完成)两个中断，TCIE,RXNEIE,IDLEIE不开启
    remap 重映射
    stop 停止位数量 0.5,1,1.5,2
    """
    @check(usart=usartChecker,baud=partial(inRange,end=7.2e6),word=lambda x:x in(8,9),irq=lambda x:x in(0,1),remap=partial(inRange,end=2),stop=usartStopChecker)
    def __init__(self,usart,baud,name=None,word=8,verify="NONE",irq=1,remap=0,stop=1):
        if not name:
            self.name = usart
        else:
            self.name = name
        tx = IO(port=USART_PORT[usart][remap][0],name="%s_TX"%self.name,mode="AFPP")
        rx = IO(port=USART_PORT[usart][remap][1],name="%s_RX"%self.name,mode="AFIN")
        self.io = [tx,rx]
        self.rcc = [usart]
        apb = 2 if usart=="USART1" else 1
        temp = 4.5e6/baud
        self.init = [
                "/*复位%s*/"%usart,
                "SET_BIT(RCC->APB%sRSTR,RCC_APB%sRSTR_%sRST);"%(apb,apb,usart),
                "CLEAR_BIT(RCC->APB%sRSTR,RCC_APB%sRSTR_%sRST);"%(apb,apb,usart),
                "/*设置波特率为%s*/"%baud,
                "%s->BRR = %s;"%(usart,int(temp)*16+int(temp-int(temp))*16),
                "/*使能%s，开启传输，开启接收*/"%usart,
                "SET_BIT(%s->CR1,USART_CR1_UE|USART_CR1_TE|USART_CR1_RE);"%usart]
        if remap:
            if remap == 2:
                self.init.append("/*设置USART3完全重映射*/")
                self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_USART3_REMAP_FULLREMAP);")
            else:
                if usart == "USART3":
                    self.init.append("/*设置USART3部分重映射*/")
                    self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_USART3_REMAP_PARTIALREMAP);")
                else:
                    self.init.append("/*设置%s重映射*/"%usart)
                    self.init.append("SET_BIT(AFIO->MAPR,AFIO_MAPR_%s_REMAP_REMAP);"%usart)
        if word == 9:
            self.init.append("/*设置字长为9*/")
            self.init.append("SET_BIT(%s->CR1,USART_CR1_M);"%usart)
        if verify != "NONE":
            self.init.append("/*设置奇偶校验*/")
            self.init.append("SET_BIT(%s->CR1,USART_CR1_PCE);"%usart)
            if verify == "ODD":
                self.init.append("/*设置奇校验*/")
                self.init.append("SET_BIT(%s->CR1,USART_CR1_PS);"%usart)
        if irq:
            self.init.append("/*开启中断*/")
            self.init.append("SET_BIT(%s->CR1,USART_CR1_RXNEIE);"%usart)
            self.init.append("NVIC->ISER[%s] = 0x20;"%usart[-1]);
        if  stop != 1:
            self.init.append("/*设置%s位停止位*/"%stop)
            self.init.append("%s_BIT(%s->CR2,USART_CR2_STOP_0);"%("CLAER" if stop==2 else "SET",usart))
            self.init.append("%s_BIT(%s->CR2,USART_CR2_STOP_1);"%("CLAER" if stop==0.5 else "SET",usart))
        self.handle = [
                "void %s_translate_a_byte(u8 byte) {"%self.name,
                "\t/*等待传输完成*/",
                "\twhile (READ_BIT(%s->SR,USART_SR_TC) == 0);"%usart,
                "\t/*发送一字节*/",
                "\t%s->DR = byte;"%usart,
                "}",
                "u8 %s_read_a_byte(void) {"%self.name,
                "\t/*等待传输完成*/",
                "\twhile (READ_BIT(%s->SR,USART_SR_RXNE) == 0);"%usart,
                "\t/*接收一字节*/",
                "\treturn %s->DR;"%usart,
                "}"]
        self.header = ["void %s_translate_a_byte(u8 byte);"%self.name,
                 "u8 %s_read_a_byte(void);"%self.name]


def iwdgPrChecker(pr):
    return pr in (4,8,16,32,64,128,256)

class IWDG(Function):
    """
    独立看门狗：独立看门狗只有一个
    pr 预分频因子 4,8,16,32,64,128,256
    rlr 重装载值 0~4095
    溢出时间(ms)：pr*rlr/40,默认1秒
    """
    @check(pr=iwdgPrChecker,rlr=partial(inRange,end=1095))
    def __init__(self,name="IWDG",pr=64,rlr=625):
        self.rcc = list() #不需要时钟
        self.io = list() #不需要io
        self.init = [
            "/*开启独立看门狗%s,溢出时间%sms*/"%(name,pr*rlr/40),
            "/*使能KR和PR写入*/",
            "IWDG->KR = 0x5555;",
            "/*写入PR*/",
            "IWDG->PR = %s;"%int(log(pr,2)-2),
            "/*写入RLR*/",
            "IWDG->RLR = %s;"%rlr,
            "/*重载*/",
            "IWDG_FEED();",
            "/*使能%s*/"%name,
            "IWDG->KR = 0xCCCC;"]
        self.handle = list()
        self.header = ["#define IWDG_FEED() IWDG->KR=0xAAAA"]


wwdgWindowCrChecker = partial(inRange,start=64,end=127)
wwdgTbChecker = lambda x:x in (1,2,4,8)
wwdgIrqChecker = lambda x:x in (0,1)

class WWDG(Function):
    """
    窗口看门狗
    窗口看门狗的启动单独使用WWDG_start()，开启后不可关闭
    window 上窗口值：64~127
    cr 计数器重装载值：64~127
    tb 预分频因子：1,2,4,8
    超时时间以pclk1=36M计算
    """
    @check(window=wwdgWindowCrChecker,cr=wwdgWindowCrChecker,tb=wwdgTbChecker,irq=wwdgIrqChecker)
    def __init__(self,window,cr,irq=0,tb=1,name="WWDG"):
        self.rcc = ["WWDG"]
        self.io = list()
        t = 4096*tb/36000
        self.init = ["/*窗口看门狗初始化，窗口%.3fms~%.3fms，%.3fms超时，%s开启中断*/"%(t*(cr-window),t*0x3F,t*cr,'' if irq else '不'),
            "WWDG->CFR = 0x%04X;"%((irq<<9)+(int(log(tb,2))<<7)+window),]
        self.handle = [
            "void %s_feed(void) {"%name,
            "\tWWDG->CR = 0x%04X;"%cr,
            "}",
            "void %s_start(void) {"%name,
            "\t%s_feed();"%name,
            "\tSET_BIT(WWDG->CR,WWDG_CR_WDGA);",
            "}"]
        self.header = ["void %s_feed(void);"%name,"void %s_start(void);"%name]


class InputCatcher(Function):
    pass

class RTC(Function):
    pass

class ADC(Function):
    pass

class DAC(Function):
    pass

class IIC(Function):

    def __init__(self,sda,scl,name="IIC"):
        self.name = name
        self.sda = IO(name="%s_SDA"%self.name,port=sda)
        self.scl = IO(name="%s_SCL"%self.name,port=scl)
        self.io = [self.sda,self.scl]
        self.rcc = list()
        self.header = [self.sda.changeMode("%s_MODE_IN()"%self.name,"AFIN"),
                self.sda.changeMode("%s_MODE_OUT()"%self.name,"PP"),
                self.sda.getInput("%s_SDA_READ"%self.name),
                self.sda.getOutput("%s_SDA_WRITE"%self.name),
                self.scl.getOutput("%s_SCL_WRITE"%self.name),
                f"void {name}_START(void);",
                f"void {name}_STOP(void);",
                "int IIC_Send_Byte(u8 byte);",
                "u8 IIC_Read_Byte(int Ack);"
                ]
        self.handle = ["""
static void {name}_delay(int n) {
\tfor(int i=0; i<n*1000; i++);
}
void {name}_START(void) {
\t{name}_MODE_OUT();
\t{name}_SDA_WRITE=1;
\t{name}_SCL_WRITE=1;
\t{name}_delay(4);
\t{name}_SDA_WRITE=0;
\t{name}_delay(4);
\t{name}_SCL_WRITE=0;
}
void {name}_STOP(void) {
\t{name}_MODE_OUT();
\t{name}_SDA_WRITE=0;
\t{name}_SCL_WRITE=0;
\t{name}_delay(4);
\t{name}_SDA_WRITE=1;
\t{name}_SCL_WRITE=1;
\t{name}_delay(4);
}
static int {name}_get_Ack(void) {
\t{name}_MODE_IN();
\t{name}_SDA_WRITE=1;
\t{name}_delay(1);
\t{name}_SCL_WRITE=1;
\t{name}_delay(1);
\tfor(int t=0; t<200; t++)
\t\tif(!{name}_SDA_READ) {
\t\t\t{name}_SCL_WRITE=0;
\t\t\treturn 0;
\t\t}
\treturn 1;
}
static void {name}_send_Ack(void) {
\t{name}_MODE_OUT();
\t{name}_SDA_WRITE=0;
\t{name}_SCL_WRITE=0;
\t{name}_delay(2);
\t{name}_SCL_WRITE=1;
\t{name}_delay(2);
\t{name}_SCL_WRITE=0;
}
static void {name}_send_NAck(void) {
\t{name}_MODE_OUT();
\t{name}_SDA_WRITE=1;
\t{name}_SCL_WRITE=0;
\t{name}_delay(2);
\t{name}_SCL_WRITE=1;
\t{name}_delay(2);
\t{name}_SCL_WRITE=0;
}
int {name}_Send_Byte(u8 byte) {                        
\t{name}_MODE_OUT();
\t{name}_SCL_WRITE=0;
\tfor(int bit=0x80; bit; bit>>=1) {
\t\t{name}_SDA_WRITE=byte&bit?1:0;
\t\t{name}_delay(2);
\t\t{name}_SCL_WRITE=1;
\t\t{name}_delay(2);
\t\t{name}_SCL_WRITE=0;
\t\t{name}_delay(2);
\t}
\tif({name}_get_Ack()) {
\t\t{name}_STOP();
\t\treturn 1;
\t} else {
\t\treturn 0;
\t}
}   
u8 {name}_Read_Byte(int Ack) {
\tu8 receive=0;
\t{name}_MODE_IN();
\tfor(int i=0; i<8; i++) {
\t\t{name}_SCL_WRITE=0;
\t\t{name}_delay(2);
\t\t{name}_SCL_WRITE=1;
\t\treceive<<=1;
\t\tif({name}_SDA_READ)receive++;
\t\t{name}_delay(1);
\t}
\tif (!ack)
\t\t{name}_send_NAck();
\telse
\t\t{name}_send_Ack();
\treturn receive;
}
""".replace("{name}",self.name)]
        self.init = []

class SPI(Function):
    pass




#########################################################################################

class AutoLib(object):

    def __init__(self):
        self.rcc = set()
        self.io = list()
        self.init = list()
        self.handle = list()
        self.header = list()

    def writeC(self):
        "写入c文件"
        with open("AutoLib.c","w") as f:
            fprint = partial(print,file=f)
            fprint(autoLibC)
            fprint("\t/*初始化时钟*/")
            for rcc in self.rcc:
                fprint("\t"+RCC[rcc])
            fprint("\n\n\n\t/*初始化io口*/")
            for io in self.io:
                for line in io.init:
                    fprint("\t"+line)
            for line in self.init:
                fprint("\t"+line)
            fprint("}")
            fprint("/*控制函数*/")
            for line in self.handle:
                fprint(line)
            fprint()

    def writeH(self):
        "写入头文件"
        with open("AutoLib.h","w") as f:
            fprint = partial(print,file=f)
            fprint(autoLibH)
            for line in self.header:
                fprint(line)
            fprint("#endif")
            fprint()

    def check(self):
        "检查错误(未完成)"

    def generate(self):
        self.check()
        self.writeC()
        self.writeH()
        
        

    def add(self,function):
        io = function.getIO()
        self.rcc = self.rcc.union(function.getRCC())
        for i in io:
            if i in self.io:
                error("io口重复占用：%s"%(i.port+str(i.pin)))
            self.rcc.add(i.getRCC()[0])
        self.io.extend(io)
        init = function.getInit()
        if init:self.init.append("")#添加空行，隔离各功能的初始化代码
        self.init.extend(init)
        handle = function.getHandle()
        if handle:self.handle.append("")#添加空行，隔离各功能的控制代码
        self.handle.extend(handle)
        header = function.getHeader()
        if header:self.header.append("")#添加空行，隔离各功能的头文件代码
        self.header.extend(header)


############################# 读取配置 ##############################
def parseConfig(lib,config):
    """
    根据标签来确定是什么功能，并添加到lib
    """
    for i in config: #使用关键字参数
        try:
            if i.tag == "gpio":
                lib.add(IO(**i.attrib))
            elif i.tag == "tim":
                lib.add(TIM(**i.attrib))
            elif i.tag == "pwm":
                lib.add(PWM(**i.attrib))
            elif i.tag == "iwdg":
                lib.add(IWDG(**i.attrib))
            elif i.tag == "wwdg":
                lib.add(WWDG(**i.attrib))
            elif i.tag == "usart":
                lib.add(USART(**i.attrib))
            elif i.tag == "iic":
                lib.add(IIC(**i.attrib))
            else:
                error("不能识别标签<%s>"%i.tag)
        except TypeError as e:
            print(e)
            error("不能识别的属性")


def main():
    """
    可以进行修改，用其他格式的配置文件
    """
    from xml.etree.ElementTree import ElementTree
    from xml.etree.ElementTree import ParseError
    try:
        config = ElementTree(file="AutoLibConfig.xml").getroot() #打开配置文件
    except ParseError as e:
        print(e)
        error("AutoLibConfig.xml：格式错误")
    except FileNotFoundError as e:
        print(e)
        error("找不到配置文件")
    lib = AutoLib()
    parseConfig(lib,config) #读取配置
    lib.generate() #生成


if __name__ == "__main__":
    #异常处理，程序失败之后显示原因
    try:
        main()
    except AutoLibException as e:
        print(e)
    except Exception as bug:
        print("BUG",bug)
    else:
        print("Generate OK!")
    input()#等待输入之后再退出

