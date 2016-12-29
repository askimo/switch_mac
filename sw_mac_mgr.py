import paramiko,time,os,re,sqlite3,threading
# maclist(id integer primary key autoincrement,mac string,sw_id integer,vlan integer,port string,bind boolean,lastfind string,info string)
# swlist(id integer primary key autoincrement,ip string,username string,password string,sw_type string,location string)
db_path=r'e:\python\macdb.db'
"""
sw_id=2
conn=sqlite3.connect(db_path)
sql='select * from swlist where id='+str(sw_id)+';'
res=conn.execute(sql).fetchall()
swid=res[0][0]
ip=res[0][1]
username=res[0][2]
password=res[0][3]
sw_type=res[0][4]
location=res[0][5]
client=paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ip,22,username,password)
chan=client.invoke_shell()
chan.send('en\r\n'+password+'\r\n')
mac_add=''
chan.send('show mac-add\r\n')
time.sleep(0.2)
res=chan.recv(2000)
mac_add+=res
print('Getting mac-address...['+str(sw_id)+']\n')
for i in range(15):
    chan.send(" ")
    time.sleep(0.2)
    res=chan.recv(10000)
    mac_add+=res
print('Get mac-address OK['+str(sw_id)+']\n')
"""
conn=sqlite3.connect(db_path)

def ssh_ruijie(sw_id):
    conn=sqlite3.connect(db_path)
    sql='select * from swlist where id='+str(sw_id)+';'
    res=conn.execute(sql).fetchall()
    swid=res[0][0]
    ip=res[0][1]
    username=res[0][2]
    password=res[0][3]
    sw_type=res[0][4]
    location=res[0][5]
    client=paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip,22,username,password)
    chan=client.invoke_shell()
    chan.send('en\r\n'+password+'\r\n')
    mac_add=''
    chan.send('show mac-add\r\n')
    time.sleep(0.2)
    res=chan.recv(2000)
    mac_add+=res
    print('Getting mac-address...['+str(sw_id)+']\n')
    for i in range(15):
        chan.send(" ")
        time.sleep(0.2)
        res=chan.recv(10000)
        mac_add+=res
    print('Get mac-address OK['+str(sw_id)+']\n')
    user_bind=''
    chan.send('show run \n')
    time.sleep(0.2)
    res=chan.recv(10000)
    user_bind+=res
    print('Getting user-bind...['+str(sw_id)+']\n')
    for i in range(15):
        chan.send(' ')
        time.sleep(0.2)
        res=chan.recv(10000)
        user_bind+=res
    print('Get user-bind OK['+str(sw_id)+']\n')
    word=re.findall(r'.{12}[a-f0-9]{4}.[a-f0-9]{4}.[a-f0-9]{4}.*/\d*',mac_add)
    find_new=0
    find_old=0
    for i in word:
        print i 
        imac=i[12:26]
        ivlan=i[1:4]
        iport=i[42:]
        print ivlan,imac,iport
        tmpres=conn.execute('select * from maclist where mac="'+imac+'" and sw_id='+str(sw_id)+' and port="'+iport+'";').fetchall()
        if tmpres==[]:
            ins_sql="insert into maclist(mac,sw_id,vlan ,port,lastfind) values('"+imac+"',"+str(sw_id)+","+str(ivlan)+",'"+str(iport)+"','"+time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+"');"
            find_new+=1
        else :
            ins_sql='update maclist set lastfind=\''+time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+'\' where id='+str(tmpres[0][0])+';'
            find_old+=1
        conn.execute(ins_sql)
    conn.commit()
    conn.close()
    return find_new,find_old

def telnet_ruijie(sw_id)
    conn=sqlite3.connect(db_path)
    sql='select * from swlist where id='+str(sw_id)+';'
    res=conn.execute(sql).fetchall()
    swid=res[0][0]
    ip=res[0][1]
    username=res[0][2]
    password=res[0][3]
    sw_type=res[0][4]
    location=res[0][5]
    #continue here
    return 0,0

    
def getmac(sw_id):
    conn=sqlite3.connect(db_path)
    sql='select * from swlist where id='+str(sw_id)+';'
    res=conn.execute(sql).fetchall()
    conn.close()
    swid=res[0][0]
    ip=res[0][1]
    username=res[0][2]
    password=res[0][3]
    sw_type=res[0][4]
    location=res[0][5]
    if sw_type == 'ssh_ruijie':
        print('SSH Connect to ruijie['+ip+'] from '+location+'\n')
        return ssh_ruijie(swid)
    elif sw_type == 'telnet_ruijie':
        print('TELNET Connect to ruijie['+ip+'] from '+location+'\n')
        return telnet_ruijie(swid)
    else :
        print 'Not portable Funtion to suit this type of switch!'
        return 0,0


def listsw():
    conn=sqlite3.connect(db_path)
    sql='select id,ip,sw_type ,location from swlist;'
    res=conn.execute(sql).fetchall()
    conn.close()
    print("id".center(5)+"ip".center(20)+"sw_type".center(18)+"   location".center(12))
    swids=[]
    for i in res:
        swids.append(str(i[0]))
        print('['+str(i[0]).center(3)+']:'+str(i[1]).center(16)+'|type:'+('['+i[2]+']').ljust(18)+' |location:'+str(i[3]).center(10))
    return swids

def flush_all_sw():
    conn=sqlite3.connect(db_path)
    res=conn.execute('select id from swlist').fetchall()
    conn.close()
    totle_new=0
    totle_old=0
    thread_list=list()
    for i in res:
        thread_list.append(threading.Thread(target=getmac,args=(i[0],)))
    thread=10
    for i in thread_list:
        thread-=1
        if thread==0:
            print('!!!!!!!!Waiting Thread!!!!!!!!!')
            time.sleep(15)
            thread=10
        i.start()
    for i in thread_list:
        i.join()


def flush_one_sw():
    swids=listsw()
    while 1 :
        choice=raw_input("Enter switch ID(0:return):")
        if choice=='0':
            return 0
        elif choice in swids:
            find_new,find_old=getmac(choice)
            print('find new mac:'+str(find_new)+'   find old mac:'+str(find_old))
        else :
            print("Error Intput!")

def find_mac_globle(mac):
    conn=sqlite3.connect(db_path)
    sql='select * from maclist where mac=\''+mac+'\';'
    res=conn.execute(sql).fetchall()
    conn.close()
    if res==[]:
        print("No MAC in this database")
    else:
        for i in res:
            print("MAC ADDRESS:"+i[1])
            print("FROM SWITCH:"+str(i[2]))
            print("SW PORT:"+i[4])
            print("IN VLAN NUM:"+str(i[3]))            
            print("LAST FIND TIMESTAMP:"+i[6])
            print("User-Bind Status:"+str(i[5]))
            print('-'*20)


def find_mac_globle_menu():
    print("**** find mac in globle ****")
    while 1:
        choice=raw_input("Enter a MAC (XXXX-XXXX-XXXX)  0-return:").lower()
        if choice=='0':
            return
        elif []==re.findall(r'^[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}$',choice):
            print("Error MAC input!")
        else:
            pass
            find_mac_globle(choice)
        
def show_database():
    conn=sqlite3.connect(db_path)
    totle=conn.execute('select count(*) from maclist').fetchall()[0][0]
    bind=conn.execute('select count(*) from maclist where bind=1').fetchall()[0][0]
    max_port=conn.execute("select count(*) n,sw_id,port from maclist group by sw_id,port order by n desc;").fetchall()
    conn.close()
    cnt=0
    mxport=""
    for i in max_port:
        if cnt==4:
            break
        mxport+=' |'+str(i[1])+':'+i[2]+' mac:'+str(i[0])+'\n'
        cnt+=1
    print('-'*20)
    print(" |Totle Mac Address:"+str(totle))
    print(" |Bind Mac Address:"+str(bind))
    print(" |MOST Mac Ports:")
    print(mxport[:-1])
    print('-'*20)
    time.sleep(1)

def init_db():
    tip="""
IMPORTANT:new database is creating.
It will create 2 tables:
1.swlist,for store switch message etc:ip,username,password,switch type,location.
2.maclist,for store mac-address message etc:mac-address,sw_id,port,bind,info.
"""
    print tip
    choice=raw_input("Confirm your choice Y/y ,OTHERS for cancel ")
    if choice in ['Y','y']:
        sql_sw=r'CREATE TABLE swlist(id integer primary key autoincrement,ip string,username string,password string,sw_type string,location string);'
        sql_mac=r'CREATE TABLE maclist(id integer primary key autoincrement,mac string,sw_id integer,vlan integer,port string,bind boolean,lastfind string,info string);'
        conn=sqlite3.connect(db_path)
        try:
            conn.execute(sql_sw)
        except sqlite3.OperationalError :
            print 'Table swlist exists . Deleting and rebuild.'
            conn.execute('drop table swlist')
            conn.execute(sql_sw)
        try:
            conn.execute(sql_mac)
        except sqlite3.OperationalError:
            print 'Table maclist exists . Deleting and rebuild.'
            conn.execute('drop table maclist')
            conn.execute(sql_mac)
        conn.commit()
        conn.close()
        print 'Finish Init DataBase.'
    else:
        print 'Operation Cancel...'

    
while 1:
    menu="""
      ############################################################
      #   [1]  list switch                                       #
      #   [2]  enter a switch                                    #
      #   [3]  find mac in globle                                #
      #   [4]  config a switch                                   #
      #   [7]  show database status                              #
      #   [8]  flush a switch mac databse(NEED 30 Sec)           #
      #   [9]  flush ALL mac database(NEED 60 Sec)               #
      #                                                          #
      #   [10] Inititial DataBase(!!!!CLEAR DATABASE!!!!)        #
      #   [0]  exit                                              #
      ############################################################
"""
    print(menu)
    choice=raw_input("      Enter Your Choice:")
    if choice=='0':
        break
    elif choice=='1':
        listsw()
    elif choice=='2':
        pass
    elif choice=='3':
        find_mac_globle_menu()
    elif choice=='4':
        pass
    elif choice=='7':
        show_database()
    elif choice=='8':
        flush_one_sw()
    elif choice=='9':
        flush_all_sw()
    elif choice=='10':
        init_db()
    else:
        continue
