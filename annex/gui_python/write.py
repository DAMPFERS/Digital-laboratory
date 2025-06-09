
MAX_FUNCTIONS = 16
count_funcs = 0



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

def generate_bin_file(filename, bin_file):
    """
    Генерирует бинарный файл в соответствии со структурой BinFile
    """
    with open(filename, 'wb') as f:
        # Запись заголовочных полей
        if bin_file.id >= 0:
            f.write(f"ID={bin_file.id}\r\n".encode('utf-8'))
        f.write(f"TYPE={bin_file.type}\r\n".encode('utf-8'))
        f.write(f"SPEED={bin_file.speed}\r\n".encode('utf-8'))
        
        # Запись текстового поля
        text = bin_file.text if bin_file.text else ""
        f.write(f'TEXT="{text}"\r\n'.encode('utf-8'))
        
        # Начало блока функций
        f.write(b"FUNC\r\n")
        
        # Запись функций
        for i in range(bin_file.function_count):
            func = bin_file.functions[i]
            prefix = f"F{func.name_func}=".encode('utf-8')
            f.write(prefix)
            
            
            # Байт количества переменных
            f.write(bytes([func.num_vars]))
            f.write(b";")
            
            # Битовая маска
            if func.bit_vector and len(func.bit_vector) == func.bit_vector_len:
                f.write(func.bit_vector)
            else:
                f.write(b"\x00" * func.bit_vector_len)
            f.write(b";")
            
            
            # Маска переменных (2 байта)
            f.write(bytes([
                func.var_mask & 0xFF,          # Младший байт
                (func.var_mask >> 8) & 0xFF     # Старший байт
            ]))
            # f.write(b";")
            f.write(b"\r\n")  # Конец строки функции
        
        # Завершение блока функций
        f.write(b"END\r\n")
        f.write(b"SCREEN\r\n")
        f.write(b"EOF")



def add_Func(name, num_vars, bit_vector, var_mask):
    
    
    func = Function()
    func.name_func = name
    func.num_vars = num_vars
    func.bit_vector_len = 1 if func.num_vars < 4 else (1 << (func.num_vars - 3))
    func.bit_vector = bit_vector  # Пример битового вектора
    func.var_mask = var_mask    # Пример маски
    
    return func
    



# Пример использования
if __name__ == "__main__":
    
    # Создаем объект файла
    bin_file = BinFile()
    bin_file.id = 3
    bin_file.type = 1
    bin_file.speed = 6
    bin_file.text = "Бугага 0_0"
    
    
    # Добавляем функции в файл
    bin_file.functions[bin_file.function_count] = add_Func(0, 3, b"\x00", 0b111)
    bin_file.function_count += 1
    bin_file.functions[bin_file.function_count] = add_Func(1, 3, b"\x0B", 0b111)
    bin_file.function_count += 1
    bin_file.functions[bin_file.function_count] = add_Func(2, 2, b"\x0A", 0b110)
    bin_file.function_count += 1
    bin_file.functions[bin_file.function_count] = add_Func(3, 4, b"KL", 0b1111)
    bin_file.function_count += 1
    
    # Генерируем файл
    generate_bin_file("generated.bin", bin_file)
    print("Файл успешно сгенерирован: generated.bin")