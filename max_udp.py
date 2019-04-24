#!/usr/bin/env python3
import socket

def canSendUDPPacketOfSize(sock, packetSize):
   ip_address = "127.0.0.1"
   port = 5005
   try:
      msg = "A" * packetSize
      if (sock.sendto(msg, (ip_address, port)) == len(msg)):
         return True
   except:
      pass
   return False

def get_max_udp_packet_size_aux(sock, largestKnownGoodSize, smallestKnownBadSize):
   if ((largestKnownGoodSize+1) == smallestKnownBadSize):
      return largestKnownGoodSize
   else:
      newMidSize = int((largestKnownGoodSize+smallestKnownBadSize)/2)
      if (canSendUDPPacketOfSize(sock, newMidSize)):
         return get_max_udp_packet_size_aux(sock, newMidSize, smallestKnownBadSize)
      else:
         return get_max_udp_packet_size_aux(sock, largestKnownGoodSize, newMidSize)

def get_max_udp_packet_size():
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   ret = get_max_udp_packet_size_aux(sock, 0, 65508)
   sock.close()
   return ret

print("Maximum UDP packet send size is", get_max_udp_packet_size())
