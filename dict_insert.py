import pymysql,re

def insert_words():
    db = pymysql.connect(host='localhost',user='root',password='123456',database='dict',charset='utf8')
    cursor = db.cursor()

    cursor.execute('use dict;')
    f =  open('/home/tarena/aid1806/dict/dict.txt','rt')
    i = 0
    while True:
        flag = True
        line = f.readline()
        # i += 1
        # print(line)
        if not line:
            flag = False
            break
        partern = r'^\w+\s+'
        # partern = r'^\s\w+'
        try:
            word_to_write = (re.match(partern,line,re.I).group()).strip()
            interpret_to_write = (line[len(word_to_write)::]).strip()
            # print(str(i)+ ' ' + word_to_write.strip()+'-->'+interpret_to_write)
        except AttributeError as e:
            continue
        try:
            # sql_insert = "insert into words(word,interpret) values('%s','%s')" % (word_to_write,interpret_to_write)
            sql_insert = "insert into words(word,interpret) values('{}','{}')".format(word_to_write,interpret_to_write)

            cursor.execute(sql_insert)
            db.commit()
            print("OK!")
        except Exception as e:
            db.rollback()
            print(e)
    f.close()
    cursor.close()
    db.close()

if __name__ == '__main__':
    insert_words()