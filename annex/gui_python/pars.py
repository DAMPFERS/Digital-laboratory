import os
import re

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ
MAX_FUNCTIONS = 16

class Function:
    def __init__(self):
        self.name_func = 0
        self.num_vars = 0
        self.bit_vector = None
        self.bit_vector_len = 0
        self.var_mask = 0

class BinFile:
    def __init__(self):
        self.id = -1
        self.type = -1
        self.speed = -1
        self.text = None
        self.functions = [Function() for _ in range(MAX_FUNCTIONS)]
        self.function_count = 0


def read_file(filename):
    """Чтение всего файла в буфер"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None
    
    size = os.path.getsize(filename)
    if size <= 0 or size > MAX_FILE_SIZE:
        print(f"Inappropriate file size: {size}")
        return None
    
    try:
        with open(filename, 'rb') as f:
            # a = f.read()
            # print(a)
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def parse_int(buf, label):
    """Парсинг целочисленного поля по метке"""
    if isinstance(buf, bytes):
        
        buf = buf.decode('utf-8', errors='ignore')
    
    pos = buf.find(label)
    if pos == -1:
        return -1
    
    num_str = ""
    pos += len(label)
    while pos < len(buf) and buf[pos].isdigit():
        num_str += buf[pos]
        pos += 1
    
    return int(num_str) if num_str else -1


def parse_quoted_text(buf, label):
    """Парсинг строки TEXT между кавычками"""
    if isinstance(buf, bytes):
        buf = buf.decode('utf-8', errors='ignore')
    
    pos = buf.find(label)
    if pos == -1:
        return None
    
    pos = buf.find('"', pos)
    if pos == -1:
        return None
    
    end_pos = buf.find('"', pos + 1)
    if end_pos == -1:
        return None
    
    return buf[pos + 1:end_pos]


def get_position_index_func(buf):
    """Поиск позиций начала и конца блока FUNC"""
    start_marker = b"FUNC\r\n"
    end_marker = b"END\r\n"
    
    start_idx = buf.find(start_marker)
    
    if start_idx == -1:
        return 0, 0
    
    end_idx = buf.find(end_marker, start_idx)
    if end_idx == -1:
        return start_idx + len(start_marker), len(buf)
    
    return start_idx + len(start_marker), end_idx


def get_count_func(buf, start, end):
    """Подсчет количества функций в блоке"""
    if start >= end:
        return 0
    return buf[start:end].count(b'\r\n')


def parse_func_block(buf, start, end, count_f):
    """Парсинг блока функций"""
    func = Function()
    if start >= end or count_f >= MAX_FUNCTIONS:
        return func
    
    # Поиск начала функции
    pos = buf.find(b'F', start, end)
    while (pos != -1) and (buf[pos+1] - int.from_bytes(b'0', byteorder='big') != count_f):
        
        if pos + 3 >= end:
            break
        
        # Проверяем формат: F<digit>=
        if buf[pos + 1:pos + 3] == b'=':
            break
        
        pos = buf.find(b'F', pos + 1, end)
        
    if pos == -1:
        return func
    
    # Извлечение данных функции
    try:
        func.name_func = buf[pos + 1] - 0x30
        if not (0 <= func.name_func <= 9):
            return func
        
        eq_pos = buf.find(b'=', pos)
        if eq_pos == -1 or eq_pos > end:
            return func
        
        func.num_vars = buf[eq_pos + 1]
        func.bit_vector_len = 1 if func.num_vars < 4 else (1 << (func.num_vars - 3))
        
        vector_start = eq_pos + 3
        vector_end = vector_start + func.bit_vector_len
        if vector_end > end:
            return func
        
        func.bit_vector = buf[vector_start:vector_end]
        
        mask_start = vector_end + 1
        if mask_start + 2 > end:
            return func
        
        func.var_mask = buf[mask_start] | (buf[mask_start + 1] << 8)
        return func
    
    except Exception as e:
        print(f"Error parsing function: {e}")
        return func


def parse_bin_file(filename):
    """Основная функция парсинга файла"""
    buf = read_file(filename)
    
    if buf is None:
        return None
    
    bfile = BinFile()
    bfile.id = parse_int(buf, "ID=")
    bfile.type = parse_int(buf, "TYPE=")
    bfile.speed = parse_int(buf, "SPEED=")
    bfile.text = parse_quoted_text(buf, "TEXT=")
    
    start_idx, end_idx = get_position_index_func(buf)
    func_count = get_count_func(buf, start_idx, end_idx)
    
    for i in range(min(func_count, MAX_FUNCTIONS)):
        func = parse_func_block(buf, start_idx, end_idx, i)
        if func.bit_vector is not None:
            bfile.functions[i] = func
            bfile.function_count += 1
    
    return bfile

def free_func_memory(bfile):
    """Очистка памяти функций"""
    if not bfile:
        return
    for i in range(bfile.function_count):
        if bfile.functions[i].bit_vector is not None:
            bfile.functions[i].bit_vector = None
    bfile.function_count = 0
    



if __name__ == "__main__":
        
    bin_file = parse_bin_file("generated.bin")

    if bin_file:
        print(f"ID: {bin_file.id}")
        print(f"Text: {bin_file.text}")
        print(f"Functions count: {bin_file.function_count}")
        
        a = (bin_file.functions[:bin_file.function_count])
        print(len(a[3].bit_vector))
        # Освобождение ресурсов
        free_func_memory(bin_file)    