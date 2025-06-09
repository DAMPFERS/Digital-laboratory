#ifndef __PARS_SUMOM
#define __PARS_SUMOM
#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>



#define MAX_FILE_SIZE (10 * 1024 * 1024)  // до 10 МБ
#define MAX_FUNCTIONS 16

typedef struct {
    uint8_t name_func;
    uint8_t num_vars;
    uint8_t *bit_vector;
    int bit_vector_len;
    uint16_t var_mask;
} Function;

typedef struct {
    int id;
    int type;
    int speed;
    char *text;
    Function functions[MAX_FUNCTIONS];
    uint8_t function_count;
} BinFile;

extern void free_buffer(void *buf);
extern char *read_file(const char *filename, long *out_size);               // Функция для чтения всего файла в буфер
extern char *read_Tail_File(const char *filename, long *out_size);          // Функция для чтения шапки файла в буфер

extern int parse_int(const char *buf, const char *label);              // Парсинг целочисленного поля по метке
extern char *parse_quoted_text(const char *buf, const char *label);    // Парсинг строки TEXT между кавычками

extern void parse_func2(const char *buf);                           // Парсинг блока FUNC…END

extern void get_Position_Index_Func(const char *buf, uint32_t* start, uint32_t* end);   // Получение индекса начала и конца блока FUNC

extern uint8_t get_Count_Func(const char *buf, uint32_t start, uint32_t end);           // Получение количества функций
extern Function get_Func_All(const char *buf, uint32_t start, uint32_t end, uint8_t count_f);  // Получение  функции, полностью

extern void free_Func_Memory(BinFile *f);

extern int sum(int a, int b);


#endif