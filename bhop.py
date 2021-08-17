from libmem import *
import keyboard

import time
import struct
import os

proc = None
local_player_offset = 0xBD0750
m_iflags_offset = 0x340
in_jump_offset = 0xBEE4E8
FL_ONGROUND = (1 << 0)

print("[+] Searching for game process...")

while True:
	if proc is None:
		try:
			pid = LM_GetProcessIdEx("hl2_linux")
			print(f"[-] Game process found: {pid}")
		except RuntimeError:
			continue

		try:
			proc = LM_OpenProcessEx(pid)
			print(f"[*] Sucessfully opened process handle")
			break
		except RuntimeError:
			print("[!] Unable to open process handle!")
			exit(-1)
	time.sleep(1)

client = LM_GetModuleEx(proc, LM_MOD_BY_STR, "cstrike/bin/client.so")
print(f"[*] Client Base: {hex(client.base)}")

local_player_addr = client.base + local_player_offset
in_jump_addr = client.base + in_jump_offset
print(f"[*] IN_JUMP address: {hex(in_jump_addr)}")

jump_data = struct.pack("@i", 6)

print("[+] Running BHOP hack")

try:
	while LM_CheckProcess(proc.pid):
		local_player = struct.unpack("@I", LM_ReadMemoryEx(proc, local_player_addr, 4))[0]
		if local_player:
			flags = struct.unpack("@i", LM_ReadMemoryEx(proc, local_player + m_iflags_offset, 4))[0]
			if keyboard.is_pressed("space") and flags & FL_ONGROUND:
				LM_WriteMemoryEx(proc, in_jump_addr, jump_data)
except BaseException as e:
	print(f"[*] Exception: \"{e}\"")
LM_CloseProcess(proc)
print("[*] Closed process handle")
print("[-] Stopped BHOP hack")
