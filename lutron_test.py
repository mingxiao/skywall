import unittest
from skywall import MyTelnetController as mtc
import subprocess
import threading

class ThreadClass(threading.Thread):
    def __init__(self,con,cmd):
        self.con =con
        self.cmd = cmd
    def run(self):
        print 'CMD:{}'.format(self.cmd)
        self.con.execute(self.cmd)
        pass

class Test(unittest.TestCase):
    def setUp(self):
        self.host = '192.168.250.1'
        self.user = 'nwk'
        self.prompt = 'QNET>'
        self.end = '\r\n'
        self.con = mtc(self.host,self.user,self.prompt,self.end)

    def test_thread(self):
        con = mtc(self.host,self.user,self.prompt,self.end,23)
        s = ['#output,77,1,100','#output,87,1,100']
##        for t in s:
##            t = ThreadClass(con,t)
##            t.start()
            #print t
    

    def test_login(self):
        """
        Test to see if we can have mulitple logins.
        We can only have one active connection at a time!
        try opening on different ports. It seems telnet only
        operates on port 23
        """
##        subprocess.call('skywall.py -s 77 -l 0',shell=True)
##        subprocess.call('skywall.py -s 87 -l 0',shell=True)
##        lvl = 0
##        con1 = mtc(self.host,self.user,self.prompt,self.end,23)
##        con1.login()
##        con1.set_level(77,lvl)
        
##        con2 = mtc(self.host,self.user,self.prompt,self.end)
##        con2.login()
##        
##
##        con3 = mtc(self.host,self.user,self.prompt,self.end)
##        con3.login()
##        
##
##        con4 = mtc(self.host,self.user,self.prompt,self.end)
##        con4.login()

        
##        con2.set_level(14,lvl)
##        con3.set_level(44,lvl)
##        con4.set_level(55,lvl)
        pass

    def test_read_file(self):
        f = 'Book1.txt'
        self.con.read_file(f)
        

if __name__=='__main__':
    unittest.main()
