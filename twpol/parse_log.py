


def parseLog(file_path, delimiter):
    f = open(file_path, "r")
    objects = []
    c_object = {}
    for line in f:
        l = line.replace("\n", "")
        if l == delimiter:
            objects.append(c_object)
            c_object = {}
        else:
            l = l.replace(" ","")
            if ":" in l:
                splitted = l.split(":")
                c_object[splitted[0]] = splitted[1]
            else:
                bonus_info = c_object.setdefault("bonus_info", [])
                bonus_info.append(l)
    return objects
