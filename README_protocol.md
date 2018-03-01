Names: Charlie Sullivan, Brian Mcmahon

Protocol design_________________________________________
Header Information:
	constant length: 40 bytes
	deliminator: '@' symbol
	information organization: 
		| Datatype | # of packets in file | Sequence Number | Size of Packet | Time to live | Options | Data |		
		Many of these fields are unused as of now but included for scalability to things like sliding window
		
		Datatype: type of message being sent (basic list)
			ACK: acknowledgement of a packet recieved
			GET: a request to get a file from the server
			PUT: Request to put a file on the server
		
		# of packets: Total packets that will be sent to make up the file desired for transport
		
		Sequence Number: This is the index number to determine the order of the packets to rebuild the file correctly
		
		Size of packet: self explanitory. Currently fixed to 100 bytes (40B for header, 60B for data)
		
		Time to live: added in because we thought it would be something we cover in the course in the future
		
		Options: auxilaray information about the packet. Typically populated with the filename
		
		Data: 60 B of payload data

Client and Server operation_____________________________
State Diagrams:
	included in repo as image files
	
Client Program flow:
	recieve command to run from ommand line
	Type of request should be indicated after the program Names
		Supported Requests (case sensitive):
			GET : get a file from the server and store it in the local directory
			PUT : store a file on the server
	filename also included as next argument in the command line
	
	GET program:	
		-send request to get a file from the server
		-wait to hear back for request acknowledgement
		-Once acknowledgement received wait for data packets to come in. 
			-store incoming data into a dictionary {key (index) : value (data)}
		-check for a blank data packet (EOF)
			-store the sorted dictionary into a file on the local machine
		
	PUT program:
		-send request to save a file on the server
		-wait for acknowledgement that server is ready to recieve the file
		-open the file and read 60 bytes at a time
			-send packet with 60 bytes and wait for acknowledgement
			-if acknowledgement arrives read next 60 bytes and send new packet
			-repeat until EOF - send empty data packet to indicate EOF
		-close file
			
Server Program Flow:

BRAIN FILLE THIS SHIT IN
			
