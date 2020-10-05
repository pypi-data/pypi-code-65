from logtools.filelog import LogFile


"""
Esta es una pruea de uso de de LogFile bajo distintas situaciones
"""
if __name__ == "__main__":
    log = LogFile("testsuma",
                  "22_MAYO_2020",
                  "pineda",
                  path="./test_logfile/")
    print("Path->", log.file_path)
    print("Filename->", log.file_name)
    a = 20
    b = 30
    c = 0
    log.info("Suma %s + %s" %(a,b))
    result_1 =  a + b
    log.info("El resultado de op 1 es : %s" %result_1)
    try:
        result_2 = b/c
    except Exception as e:
        log.exception("Error en la dvisión %s" %e)
