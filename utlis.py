# encoding: UTF-8
import ctypes

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [('dwSize',ctypes.c_uint32),('bVisible',ctypes.c_bool)]

class SMALL_RECT(ctypes.Structure):  
    _fields_ = [('Left', ctypes.c_short),  
               ('Top', ctypes.c_short),  
               ('Right', ctypes.c_short),  
               ('Bottom', ctypes.c_short),  
              ]  
  
class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):  
    _fields_ = [('dwSize', COORD),  
               ('dwCursorPosition', COORD),  
               ('wAttributes', ctypes.c_uint),  
               ('srWindow', SMALL_RECT),  
               ('dwMaximumWindowSize', COORD),  
              ]  

STD_OUTPUT_HANDLE= -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def SetConsoleCursorPosition(x,y):
    dwCursorPosition = COORD()
    dwCursorPosition.X = x
    dwCursorPosition.Y = y
    ctypes.windll.kernel32.SetConsoleCursorPosition(std_out_handle,dwCursorPosition)

def SetConsoleCursorInfo(bVisible):
    pcci = CONSOLE_CURSOR_INFO()
    ctypes.windll.kernel32.GetConsoleCursorInfo(std_out_handle,ctypes.pointer(pcci))
    pcci.bVisible = bVisible
    ctypes.windll.kernel32.SetConsoleCursorInfo(std_out_handle,ctypes.pointer(pcci))

def GetConsoleCursorPosition():
    sbi = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(std_out_handle,ctypes.byref(sbi))
    return sbi.dwCursorPosition.X,sbi.dwCursorPosition.Y

#https://github.com/theinternetftw/xyppy/blob/master/xyppy/term.py
def WriteConsoleOutputCharacter(info,x,y):
    dwCursorPosition = COORD()
    dwCursorPosition.X = x
    dwCursorPosition.Y = y
    written = ctypes.c_uint(0)
    ctypes.windll.kernel32.WriteConsoleOutputCharacterA(std_out_handle,ctypes.c_char_p(info),len(info),dwCursorPosition,ctypes.byref(written))