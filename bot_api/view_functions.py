def serializer_error(dict_element):
    k = []
    r = ''
    for i, j in dict_element:
        k += j
    for i in k:
        r += i + ', '
    r = r[:-2]
    response = {"status": False, "message": r}
    return response