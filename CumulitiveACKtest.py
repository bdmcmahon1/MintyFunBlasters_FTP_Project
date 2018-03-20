#cumulitive ack testing module

acklist=[]
ackindex=0
lastACK=0

while 1:
	current_ack = int(raw_input("Enter an packet number: "))
	if current_ack == 99:
		break
	
	if current_ack in acklist:
		print'duplicat message - ignore'
		continue
	
		
		
	
	
	acklist.append(current_ack)
	print acklist
	if 1 not in acklist:
		print 'still waiting on first packet in sequence'
		continue
		
	print 'sorting list of acks recieved'
	sorted_acklist = sorted(acklist)
	print sorted_acklist
	
	
	print 'checking for missing acks'
	#test to see if all the acks are there
	
	#finalcheck is number of times for loop should iterate if all is good
	finalCheck = len(sorted_acklist)-lastACK
	cnt=0
	if len(sorted_acklist)>1:
		for i in range(lastACK,len(sorted_acklist)):
			print 'checking index %d' % i
			check=sorted_acklist[i]-sorted_acklist[i-1]
			
			if check > 1:
				
				print 'missing a message'
				bestACK = sorted_acklist[i-1]
				if bestACK == lastACK:
					print 'previous ACK sent still best cumulitive ACK'
					break
				else:
					print 'Best cumulitive ack possible: %d' % sorted_acklist[i-1]
					print 'sending best cumulitive ack'
					break
			#ISSUE HERE - IF LAST NUMBER REPEAT IT WONT CHECK THE END OF THE LIST
			
				
			
			
			bestACK = sorted_acklist[i]	
			lastACK = bestACK
		#if the for loop finishes without missing packets
			cnt=cnt+1
			
			#check if everything went smoothly and it is the final check of the for loop (highest ack receieved)

	
	#else:
		#if acklist[ackindex] == 1:
			#print 'first packet recieved - ACK sent'
			#lastACK=1
		#else:
			#print 'first packet recieved not first packet sent \ndont send ack - Waiting for more packets'
			##lastACK = 1
			##not sure how to handle the inisial part being 0 - for loop affected
	
	if cnt == finalCheck:
		print 'All messages present - latest message is best ack \n Send ack for message latest message recieved: %d' % bestACK
	
	ackindex = ackindex+1
	print 'ready for another message'
	
