#include "pars.h"




int main() {
    
    BinFile file_1 = {0};
    long size;
    char *buf = read_file("test.bin", &size);
    if (!buf) return 1;

    int id    = parse_int(buf, "ID=");
    int type  = parse_int(buf, "TYPE=");
    int speed = parse_int(buf, "SPEED=");
    printf("ID    = %d\n", id);
    printf("TYPE  = %d\n", type);
    printf("SPEED = %d\n", speed);

    char *text = parse_quoted_text(buf, "TEXT=");
    if (text) {
        printf("TEXT  = \"%s\"\n", text);
        free(text);
    } else {
        printf("TEXT не найден\n");
    }

    file_1.id = id;
    file_1.type = type;
    file_1.speed = speed;
    file_1.text = text;

    printf("id= %d, type= %d, speed= %d, text: %s\r\n", file_1.id, file_1.type, file_1.speed, file_1.text);

    // parse_func2(buf);
    uint32_t start;
    uint32_t end;

    get_Position_Index_Func(buf, &start, &end);
    file_1.function_count = get_Count_Func(buf, start, end);
    for (int i = 0; i < file_1.function_count; i++){
        file_1.functions[i] = get_Func_All(buf, start, end, i);
        printf("F%d: var: %d, mask: %d \r\n", file_1.functions[i].name_func, file_1.functions[i].num_vars, file_1.functions[i].var_mask);
    }
    


    
    

    free_Func_Memory(&file_1);

    free(buf);
    return 0;
}