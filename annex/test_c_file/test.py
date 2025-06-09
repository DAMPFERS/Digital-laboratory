import ctypes
import os







# Определяем структуры данных
class Function(ctypes.Structure):
    _fields_ = [
        ("name_func", ctypes.c_uint8),
        ("num_vars", ctypes.c_uint8),
        ("bit_vector", ctypes.POINTER(ctypes.c_uint8)),
        ("bit_vector_len", ctypes.c_int),
        ("var_mask", ctypes.c_uint16)
    ]

class BinFile(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("type", ctypes.c_int),
        ("speed", ctypes.c_int),
        ("text", ctypes.c_char_p),
        ("functions", Function * 16),  # MAX_FUNCTIONS = 16
        ("function_count", ctypes.c_uint8)
    ]


# Загружаем стандартную библиотеку C для работы с памятью
libc = ctypes.CDLL('msvcrt')  # Для Windows (MSVC)
libc.free.argtypes = [ctypes.c_void_p]
libc.free.restype = None


# Загружаем DLL
parser = ctypes.CDLL("./pars.dll")

# Определяем типы функций
parser.read_file.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_long)]
parser.read_file.restype = ctypes.POINTER(ctypes.c_char)

parser.parse_int.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
parser.parse_int.restype = ctypes.c_int

parser.parse_quoted_text.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
parser.parse_quoted_text.restype = ctypes.c_char_p

parser.get_Position_Index_Func.argtypes = [
    ctypes.c_char_p, 
    ctypes.POINTER(ctypes.c_uint32), 
    ctypes.POINTER(ctypes.c_uint32)
]
parser.get_Position_Index_Func.restype = None

parser.get_Count_Func.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
parser.get_Count_Func.restype = ctypes.c_uint8

parser.get_Func_All.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8]
parser.get_Func_All.restype = Function

parser.free_Func_Memory.argtypes = [ctypes.POINTER(BinFile)]
parser.free_Func_Memory.restype = None

parser.free_buffer.argtypes = [ctypes.c_void_p]  # Используем void* для универсальности
parser.free_buffer.restype = None

# Инициализируем структуру BinFile
file_1 = BinFile()
ctypes.memset(ctypes.byref(file_1), 0, ctypes.sizeof(file_1))

# Читаем файл
# Читаем файл
size = ctypes.c_long(0)
file_path = os.path.abspath("test.bin").encode('utf-8')
buf_ptr = parser.read_file(file_path, ctypes.byref(size))

if not buf_ptr:
    print("Failed to read file")
    exit(1)

buf_char_p = ctypes.cast(buf_ptr, ctypes.c_char_p)

# Парсим основные поля
id_val = parser.parse_int(buf_char_p, b"ID=")
type_val = parser.parse_int(buf_char_p, b"TYPE=")
speed_val = parser.parse_int(buf_char_p, b"SPEED=")

print(f"ID    = {id_val}")
print(f"TYPE  = {type_val}")
print(f"SPEED = {speed_val}")

# Парсим текстовое поле - ВАЖНОЕ ИЗМЕНЕНИЕ
text_ptr = parser.parse_quoted_text(buf_char_p, b"TEXT=")
if text_ptr:
    try:
        # Получаем строку напрямую через ctypes
        text = ctypes.c_char_p(text_ptr).value.decode('utf-8')
        print(f'TEXT  = "{text}"')
        print("TEXT processed")
    finally:
        # Освобождаем память через СТАНДАРТНУЮ библиотеку C
        print("Freeing text memory")
        
        print("Memory freed")
else:
    print("TEXT не найден")
    text = None

print("OUT")

# Заполняем структуру BinFile
file_1.id = id_val
file_1.type = type_val
file_1.speed = speed_val
file_1.text = text.encode('utf-8') if text else None

# Парсим функции
start = ctypes.c_uint32(0)
end = ctypes.c_uint32(0)
parser.get_Position_Index_Func(buf_char_p, ctypes.byref(start), ctypes.byref(end))

file_1.function_count = parser.get_Count_Func(buf_char_p, start.value, end.value)

print(f"Found {file_1.function_count} functions")

for i in range(file_1.function_count):
    func = parser.get_Func_All(buf_char_p, start.value, end.value, i)
    file_1.functions[i] = func
    
    # Печатаем информацию о функции
    print(f"F{func.name_func}: var: {func.num_vars}, mask: {func.var_mask}")
    
    # Печатаем битовый вектор
    if func.bit_vector and func.bit_vector_len > 0:
        # Создаем безопасный буфер
        buffer_type = ctypes.c_uint8 * func.bit_vector_len
        buffer = ctypes.cast(func.bit_vector, ctypes.POINTER(buffer_type)).contents
        vector_bytes = bytes(buffer)
        print(f"  Bit vector ({func.bit_vector_len} bytes): {vector_bytes.hex()}")

# Освобождаем память
print("Freeing function memory...")
parser.free_Func_Memory(ctypes.byref(file_1))

print("Freeing main buffer...")




print(1)
libc.free(buf_ptr)
print(2)
libc.free(text_ptr)
print(3)
parser.free_buffer(ctypes.cast(buf_ptr, ctypes.c_void_p))
print("Main buffer freed")

print("All operations completed successfully")