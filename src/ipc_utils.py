import struct
from multiprocessing import shared_memory
from typing import Optional

def create_shared_memory(name: str, size: int) -> shared_memory.SharedMemory:
    """Create a new shared memory block."""
    try:
        shm = shared_memory.SharedMemory(name=name, create=True, size=size)
        return shm
    except FileExistsError:
        # If it exists, connect to it and unlink it first, then recreate
        shm = shared_memory.SharedMemory(name=name)
        shm.unlink()
        return shared_memory.SharedMemory(name=name, create=True, size=size)

def get_shared_memory(name: str) -> shared_memory.SharedMemory:
    """Connect to an existing shared memory block."""
    return shared_memory.SharedMemory(name=name)

def write_string_to_memory(shm: shared_memory.SharedMemory, data: str):
    """Write a string to shared memory, prefixing it with its 4-byte length."""
    encoded_data = data.encode('utf-8')
    data_length = len(encoded_data)
    
    if data_length + 4 > shm.size:
        raise ValueError(f"Data size ({data_length + 4} bytes) exceeds shared memory size ({shm.size} bytes).")
        
    # Write 4-byte length prefix
    shm.buf[:4] = struct.pack('!I', data_length)
    # Write the actual data
    shm.buf[4:4+data_length] = encoded_data

def read_string_from_memory(shm: shared_memory.SharedMemory) -> str:
    """Read a string from shared memory, using the 4-byte length prefix."""
    # Read the 4-byte length prefix
    data_length = struct.unpack('!I', shm.buf[:4])[0]
    
    if data_length > shm.size - 4:
        raise ValueError("Memory corrupted or size exceeds block boundary.")
        
    encoded_data = bytes(shm.buf[4:4+data_length])
    return encoded_data.decode('utf-8')

def cleanup_shared_memory(shm: shared_memory.SharedMemory):
    """Safely close and unlink a shared memory block."""
    try:
        shm.close()
        shm.unlink()
    except FileNotFoundError:
        pass # Already unlinked
