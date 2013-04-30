"""
TODO:
1. Implement the area command
2. Turn all lights on at once faster
"""
import telnetlib
import argparse
import re

class MyTelnetController:
    """
    This controller is based on http://www.goldb.org/telnetpython.html

    Modified to fit our needs
    """
    def __init__(self,host,username,prompt,end):
        """
        Constructor. For the Lutron QSE-CI-NWK-E, we do not need a password
            
        @param host_name: Host name or IP address
        @param user_name: User name 
        @param prompt: Command prompt (or partial string matching the end of the prompt)
        @param end: String indicating end of command
        """
        assert host.find('.') > 1  #dumb IP address check
        assert username in ['nwk','nwk2'] #we know it's either one of those two
        self.HOST=host
        self.USER=username
        self.PROMPT=prompt
        self.END=end
        self.TN = None

    def login(self):
        """
        Login to Lutron Hub via telnet
        """
        try:
            self.tn = telnetlib.Telnet(self.HOST)
            self.tn.read_until('login: ') #this should always appear
            self.tn.write(self.USER +self.END) #how can we check for correct username?
            self.tn.read_until('connection established') #should appear if connection successful
        except:
            print 'ERROR: Invalid hostname or system timeout'

    def set_level(self,light_id,level):
        """
        Sets a light fixture to a particular level
        """
        level = int(level)
        cmd = "#output,%s,1,%s"%(light_id,level)
        return self.execute(cmd)

    def set_area(self,area,level):
        cmd = '#area,{},1,{}'.format(area,level)
        return self.execute(cmd)

    def get_level(self,light_id):
        cmd = '?output,%s,1'%light_id
        return self.execute(cmd)
    
    def execute(self,command):
        """
        Generic command executer.
        @param command - String command to be executed
        """
        assert command[0] in ['#','?','~'] #command indicators defined by Lutron
        self.tn.write(command+self.END)
        response = self.tn.read_until(self.PROMPT)
        #make sure you have the correct PROMPT, otherwise we will wait indefinitely
        self.check_response(response)
        return self.__strip_output(command,response)

    def logout(self):
        self.tn.close()

    def __strip_output(self,command,response):
        """Strip everything from the response except the actual command output.
            
        @param command: Unix command        
        @param response: Command output
        @return: Stripped output
        @rtype: String
        """
        lines=response.splitlines()
        #if command was echoed back remove it
        if command in lines[0]:
            lines.pop(0)
        #remove last element, its just the command prompt
        lines.pop()
        return ''.join(lines)

    def check_response(self,response):
        """
        Check if the reponse contains an error message.
        Error messages take the format:~ERROR,<num>
        Where <num> in [1,2,3,4,5]. Documented in Lutron Integration Protocol pg.26

        Prints error meaning if present, otherwise do nothing
        
        @param response: Command output
        """
        pat = re.compile(r"ERROR,([1-5])")
        m = pat.search(response)
        if m is not None:
            errno = int(m.group(1))
            if errno == 1:
                pass
            elif errno == 2:
                print 'Light fixture number probably invalid'
            elif errno == 3:
                pass
            elif errno == 4:
                print 'Light Levels out of range'
            elif errno == 5:
                pass

if __name__ == '__main__':
    host = '192.168.250.1'
    user = 'nwk'
    prompt = 'QNET>'
    end = '\r\n'
    #setup parsers. Could go in its own method
    parser = argparse.ArgumentParser(description = "Set or Get light levels.",
                                     epilog="Host:192.168.250.1, user:nwk")
    group= parser.add_mutually_exclusive_group()
    group.add_argument('-s','--set', help='ID of light fixture to set')
    group.add_argument('-g','--get', help='ID of light fixture to get')
    group.add_argument('-a','--area',help='ID of area to set')
    parser.add_argument('-l','--level',help='Light level to set a fixture to')
    args = parser.parse_args()
    if args.set:
        if args.level is None:
            parser.error('Light level, -l, is required when setting a fixture')
        else:
            con = MyTelnetController(host,user,prompt,end)
            con.login()
            print con.set_level(args.set,int(args.level))
            con.logout()
    if args.get:
        con = MyTelnetController(host,user,prompt,end)
        con.login()
        print con.get_level(args.get)
        con.logout()
    if args.area and args.level:
        con = MyTelnetController(host,user,prompt,end)
        con.login()
        con.set_area(args.area,args.level)
        con.logout()
