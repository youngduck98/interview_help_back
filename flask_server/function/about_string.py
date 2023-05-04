def make_list_to_string(input_list):
    ret_str = ""
    for element in input_list:
        ret_str += element + ','
    ret_str = ret_str[0:-1]
    return ret_str