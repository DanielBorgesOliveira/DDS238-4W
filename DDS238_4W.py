#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Referencies:
# http://domoticx.com/modbus-kwh-meter-dds238-1-zn/

# Dependencies: 
# pip install pymodbus
from pymodbus.client.sync import ModbusSerialClient

class DDS238_4W:
    '''
    # Name;         Unit;               Address;    Count;  Addres in Decimal
    # Total         [kWh * 100];        0x0000;         2   0   
    # Export        [KWh * 100];        0.0008;         2   8
    # Import        [KWh * 100];        0x000A;         2   10
    # Voltage       [V * 10];           0x000C;         1   12
    # Current       [A * 100];          0x000D;         1   13
    # Active Power  [W];                0x000E;         1   14
    # Reacive Power [W];                0x000F;         1   15
    # Power Factor  [cos(phi) * 1000];  0x0010;         1   16
    # Frequency     [Hz * 100];         0x0011;         1   17
    '''
    def __init__(
        self,
        DeviceAddress,
        client,
    ):
        self.DeviceAddress = DeviceAddress
        self.client = client
    
    def ReadTotalWork(self):
        
        address=0x0000
        count=2
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/100.
    
    def ReadVoltage(self):
        
        address=0x000C
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/10.
    
    def ReadAmperage(self):
        
        address=0x000D
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/100.
    
    def ReadActivePower(self):
        
        address=0x000E
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]  
    
    def ReadReactivePower(self):
        
        address=0x000F
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]
    
    def ReadPowerFactor(self):
        
        address=0x0010
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/1000.
    
    def ReadFrequency(self):
        
        address=0x0011
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/100.

if __name__ == "__main__":
    client = ModbusSerialClient(
        method = "rtu",
        port = ('/dev/ttyUSB1'),
        stopbits = 1,
        bytesize = 8,
        parity = "N",
        baudrate = 9600,
        timeout = 1,
        retries = 2
    )
    client.connect()
    device01 = DDS238_4W(DeviceAddress = 0x01, client = client)
    
    # Get the values.
    device01.ReadTotalWork()
    device01.ReadVoltage()
    device01.ReadAmperage()
    device01.ReadActivePower()
    device01.ReadReactivePower()
    device01.ReadPowerFactor()
    device01.ReadFrequency()



















