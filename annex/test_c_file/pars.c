#include "pars.h"









void free_buffer(void *buf) {
    if (buf) {
        free(buf);
    }
}


// Функция для чтения всего файла в буфер
char *read_file(const char *filename, long *out_size) {
    FILE *f = fopen(filename, "rb");
    if (!f) {
        perror("Unable to open file");
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (size <= 0 || size > MAX_FILE_SIZE) {
        printf("Inappropriate file size: %ld\n", size);
        fclose(f);
        return NULL;
    }
    char *buf = malloc(size + 1);
    if (!buf) {
        perror("malloc");
        fclose(f);
        return NULL;
    }
    fread(buf, 1, size, f);
    fclose(f);
    buf[size] = '\0';
    if (out_size) *out_size = size;
    return buf;
}

// Парсинг целочисленного поля по метке
int parse_int(const char *buf, const char *label) {
    char *p = strstr(buf, label);
    if (!p) return -1;
    p += strlen(label);
    return (int)strtol(p, NULL, 10);
}

// Парсинг строки TEXT между кавычками
char *parse_quoted_text(const char *buf, const char *label) {
    char *p = strstr(buf, label);
    if (!p) return NULL;
    p = strchr(p, '"');
    if (!p) return NULL;
    char *q = strchr(p + 1, '"');
    if (!q) return NULL;
    size_t len = q - p - 1;
    char *out = malloc(len + 1);
    if (!out) return NULL;
    memcpy(out, p + 1, len);
    out[len] = '\0';
    return out;
}


void get_Position_Index_Func(const char *buf, uint32_t* start, uint32_t* end){
    uint32_t _start;
    uint32_t _end;

    for(_end = 0; !((*(buf + _end) == 'E') && (*(buf + _end + 1) == 'N') && (*(buf + _end + 2) == 'D')); ++_end)
        if(((*(buf + _end) == 'F') && (*(buf + _end + 1) == 'U') && (*(buf + _end + 2) == 'N') && (*(buf + _end + 3) == 'C')))
            _start = _end + strlen("FUNC\n\r");

    *start = _start;
    *end = _end;
    return;


}



uint8_t get_Count_Func(const char *buf, uint32_t start, uint32_t end){

    uint8_t count_func = 0;
    for(int i = start; i < end; ++i){
        if((*(buf + i ) == '\r') && (*(buf + i + 1) == '\n')) 
            count_func++;  
    }
    return count_func;
}


Function get_Func_All(const char *buf, uint32_t start, uint32_t end, uint8_t count_f){

    Function file_func;
    const char *func_str;
    func_str = &buf[start];

    uint8_t index_count = 0;

    while(1){
        if(*func_str == 'F'){
            ++func_str;
            if (index_count != count_f) {
                
                index_count++;
                while(*(func_str++) != 'F')
                    ;
                func_str--;
                continue;
            }

            file_func.name_func = (uint8_t)*func_str - '0';
            break;
        }
    } 

    if(*(++func_str) == '='){
        ++func_str;
        file_func.num_vars = (uint8_t)*(func_str++); // записали байт с количеством переменных
        file_func.bit_vector_len = (file_func.num_vars < 4 ) ? 0x0001 : (1 << (file_func.num_vars - 3)); // вычисляем размер таблицы истинности в байтах
            
        file_func.bit_vector = (uint8_t*)malloc(file_func.bit_vector_len * sizeof(uint8_t));   // выделяем память под таблицу истинности 
        if (file_func.bit_vector == NULL) {
            perror("malloc");
            return file_func;
        }

        for (uint16_t i = 0; i < file_func.bit_vector_len; i++){
            *(file_func.bit_vector++) = *(++func_str);                  // записываем битовый вектор в выделенный масив
                // if (i < file_func.bit_vector_len - 1 ) file_func.bit_vector++;
        }
        file_func.bit_vector -= file_func.bit_vector_len;               // Возвращаем указатель в начало
        // printf("%c \r\n", file_func.bit_vector[0]);
        ++func_str;

        file_func.var_mask = (uint16_t)*(++func_str);
            
            
        file_func.var_mask |= (uint16_t)*(++func_str) << 8; 


        ++func_str;
        ++func_str;
        ++func_str;
        return file_func;
        }
    
    

}




void free_Func_Memory(BinFile *f){
    for (uint8_t i = 0; i < f->function_count; i++)
        free(f->functions[i].bit_vector);
}



int sum(int a, int b){
    return a + b;
}