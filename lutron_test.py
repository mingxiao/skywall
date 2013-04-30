import unittest
from skywall import MyTelnetController as mtc

class Test(unittest.TestCase):
    def setUp(self):
        self.host = '192.168.250.1'
        self.user = 'nwk'
        self.prompt = 'QNET>'
        self.end = '\r\n'

    def test_login(self):
        """
        Test to see if we can have mulitple logins.
        We can only have one active connection at a time!
        try opening on different ports. It seems telnet only
        operates on port 23
        """
        lvl = 0
        con1 = mtc(self.host,self.user,self.prompt,self.end,23)
        con1.login()
        con1.set_level(77,lvl)
        
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

if __name__=='__main__':
    unittest.main()
