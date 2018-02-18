ys, re                                                                                   
 8import time                                                                            
 9import select                                                                          
10                                                                                       
11def usage():                                                                           
12    print "usage: %s [--serverAddr host:port]"  % sys.argv[0]                          
13    sys.exit(1)                                                                        
14                                                                                       
15try:                                                                                   
16    args = sys.argv[1:]                                                                
17    while args:                                                                        
18        sw = args[0]; del args[0]                                                      
19        if sw == "--serverAddr":                                                       
20            addr, port = re.split(":", args[0]); del args[0]                           
21            serverAddr = (addr, int(port))                                             
22        else:                                                                          
23            print "unexpected parameter %s" % args[0]                                  
24            usage();                                                                   
25except:                                                                                
26    usage()                                                                            
27                                                                                       
28                                                                                       
29#create clientSocket object                                                            
30clientSocket = socket(AF_INET, SOCK_DGRAM)                                             
31clientSocket.setblocking(0)      #set blocking to false so timeouts work               
32                                                                                       
33#set up client socket to recieve                                                       
34#get input from the user                                                               
35message = raw_input("Input lowercase msg:")                                            
36                                                                                                     
37#set up lists to be used in select function for reading msgs from server                             
38readSock = [clientSocket]                                                                            
39writeSock = []      #empty list since we arent writing to sockets (used in queue?)                   
40errorSock=[]        #empty list - not interested in errors from select                               
41timeout=5           #time out variable since select has timeout built in                             
42                                                                                                     
43                                                                                                     
44                                                                                                     
45                                                                                                     
46#mark start time for RTT calc                                                                        
47#startTime=time.time()                                                                               
48#send the data to the server                                                                         
49clientSocket.sendto(message, serverAddr)                                                             
50print "message sent. Ready to recieve"                                                               
51                                                                                                                            ^
52#recieve message from server                                                                         
53                                                                                                     
54readReady, writeReady, errorReady = select(readSock,writeSock,errorSock,timeout)                     
55#if nothing is present in the sockets print a timeout error                                          
56if not readReady and not writeReady and not errorReady:                                                                     ^
57    print "timeout: No communication from the server"                                                
58#if there is something present in the read sockets read it and print it out                          
59for socket in readReady:                                                                             
60    #dont forget to calculate RTT for the message                                                    
61    #RTT = startTime-time.time()                 
