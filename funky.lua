-- adrian protocol example
-- author: Adrian Veliz

local charlie_proto = Proto("charlie","Charlie Protocol")

-- create a function to dissect it
function charlie_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "CHARLIE"
    local subtree = tree:add(charlie_proto,buffer(),"Charlie Protocol Data")
	
	-- Message is at least three bytes long
	if buffer:len() < 3 then
		subtree:add_expert_info(PI_MALFORMED, PI_ERROR, "Invalid Message")
		return end
	
	--split file header
	
	--attempt to split the message (is it subtree)
	--local splitMsg = split("insert string here", "@")
	-- All messages have a sequence number and type
    local seq_num = buffer(0,1):uint()
    local msg_type = buffer(0,3):string() 
    local message = buffer(0):string()
    
    local var=0 ; j = 1; msg_split = {}
--    local hdr_list = {"Datatype" , "# of packets in file" , "Sequence Number" , "Size of Packet" , "Time to live" , "Options" , "Data" }
   if msg_type == "DAT" then
     --add this is a get message subt
     subtree:add(buffer(0,3), "Data Message")
     --hilight DAT in the overall message with the buffer bit
     --display get request in the protocol subtree
     --split message and display all fields in the subtree
     local payload  = buffer(4):string()
     local strings = mysplit(payload, "@")
     for k,v in pairs(strings) do
       subtree:add(buffer(1,1),v)
     end
   elseif msg_type == "GET" then
     subtree:add(buffer(4), "Get Request")
     --now slit the message into the different sections of the headers and display them
     local payload  = buffer(4):string()
     local strings = mysplit(payload, "@")
     for k,v in pairs(strings) do
       subtree:add(buffer(1,1),v)
     end
   else
     subtree:add(buffer(3), "Put request")
     --split message and display for any tupe of message just to see what is going on
     local payload  = buffer(4):string()
     local strings = mysplit(payload, "@")
     for k,v in pairs(strings) do
       subtree:add(buffer(1,1),v)
     end
   end
   
    --subtree:add(buffer(0,1),"Sequence Number: " .. seq_num)
    --subtree:add(buffer(1,1),"Type: " .. msg_type)
	
	
	--ORIGINAL SCRIPT HERE (COMMENTIED BELOW OUT OF THE WAY)
  
end
-- load the udp.port table
udp_table = DissectorTable.get("udp.port")
-- register protocol to handle udp ports
--make sure these parts are the ones you are using for your server and client
udp_table:add(25000,charlie_proto)
udp_table:add(50000,charlie_proto) 
udp_table:add(5002,charlie_proto)



function mysplit(inputstr, sep)
        if sep == nil then
                sep = "%s"
        end
        local t={} ; i=1
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
                t[i] = str
                i = i + 1
        end
        return t
end
 
-- original source code and getting started
-- https://shloemi.blogspot.com/2011/05/guide-creating-your-own-fast-wireshark.html

-- helpful links
-- https://delog.wordpress.com/2010/09/27/create-a-wireshark-dissector-in-lua/
-- https://wiki.wireshark.org/LuaAPI/Tvb
-- http://lua-users.org/wiki/LuaTypesTutorial
-- https://wiki.wireshark.org/Lua/Examples
-- https://wiki.wireshark.org/LuaAPI/Proto
-- https://www.wireshark.org/docs/wsdg_html_chunked/wslua_dissector_example.html
-- https://www.wireshark.org/lists/wireshark-users/201206/msg00010.html
-- https://wiki.wireshark.org/LuaAPI/TreeItem
-- https://www.wireshark.org/docs/man-pages/tshark.html

--[[
 if datatype == "GET" then  	-- request file
		subtree:add(buffer(2), "GET Request" .. buffer(2):string())
		--subtree:add_expert_info(PI_RESPONSE_CODE, PI_WARN, "File not found")
	elseif datatype == "PUT" then -- put a file
		subtree:add(buffer(2), "PUT request" .. buffer(2):string())
	elseif datatype == "DATA" then 	-- Sending Data
		subtree:add(buffer(2),"DATA: " .. buffer(2))
		--now i have to care about sequence number
	if msg_type == "F" then						-- Last Data
			subtree:add_expert_info(PI_RESPONSE_CODE, PI_NOTE, "Finished sending")
		end
	else						-- Unknown message type	
		subtree:add_expert_info(PI_PROTOCOL, PI_WARN, "Unknown message type")
		subtree:add(buffer(0),"ERROR: " .. buffer(0))
	end
	--]]
