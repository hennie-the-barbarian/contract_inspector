def is_txt(file):
    try:
        file.readline()
        return True
    except:
        return False
    
def get_muni():
    return "Minneapolis, MN"