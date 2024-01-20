#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# /usr/bin/screen -S EnergyMeter -m -d /bin/bash -c 'sleep 15 && /root/medidor.py'

# http://domoticx.com/modbus-kwh-meter-dds238-1-zn/
 
# pip install pymodbus mysqlclient

''' ****************** SQL commands  ****************** 
CREATE DATABASE iot;

CREATE USER 'iot'@'localhost' IDENTIFIED BY 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';
CREATE USER 'iot'@'%' IDENTIFIED BY 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';
CREATE USER 'iot'@'10.0.1.5' IDENTIFIED BY 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';


# If mysql 8
GRANT ALL ON iot.* TO 'iot'@'localhost';
GRANT ALL ON iot.* TO 'iot'@'%';
GRANT ALL ON iot.* TO 'iot'@'10.0.1.5';
alter user 'iot'@'localhost' identified with mysql_native_password by 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';
alter user 'phpmyadmin'@'%' identified with mysql_native_password by 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';
# else
#GRANT ALL PRIVILEGES ON iot.* TO 'iot'@'localhost' IDENTIFIED BY 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';
#GRANT ALL PRIVILEGES ON iot.* TO 'iot'@'%' IDENTIFIED BY 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';
#GRANT ALL PRIVILEGES ON iot.* TO 'iot'@'10.0.1.5' IDENTIFIED BY 'r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ';

# https://stackoverflow.com/questions/9353087/reset-mysql-init-connect-values
SET GLOBAL init_connect='';

FLUSH PRIVILEGES;

CREATE TABLE `iot`.`EnergyMeter` ( `id` INT(11) NOT NULL AUTO_INCREMENT , `data` INT(11) NOT NULL COMMENT 'A data é o número de segundos desde do epoch.' , `MeterID` INT(3) NOT NULL COMMENT 'ID do medidor no barramento rs485' , `Voltage` FLOAT(10) NOT NULL COMMENT 'Tensão real [V].' , `Current` FLOAT(10) NOT NULL COMMENT 'Corrente real [A].' , `ActivePower` FLOAT(10) NOT NULL COMMENT 'Potência Ativa [KW]' , `ReactivePower` FLOAT(10) NOT NULL COMMENT 'Potência Reativa [KW]' , `PowerFactor` FLOAT(10) NOT NULL COMMENT 'Fator de Potência [º]' , `Frequency` FLOAT(10) NOT NULL COMMENT 'Frequência da rede [Hz].' , PRIMARY KEY (id)) ENGINE = InnoDB;

ALTER TABLE `EnergyMeter` ADD `TotalWork` INT(12) NOT NULL COMMENT 'Consumo acumulado [KWh].' AFTER `MeterID`;


CREATE TABLE `iot`.`HumidityMeter` (
`id` INT(11) NOT NULL AUTO_INCREMENT,
`time` INT(11) NOT NULL COMMENT 'O número de segundos desde do epoch.',
`MeterID` INT(3) NOT NULL COMMENT 'ID do medidor no barramento rs485',
`Temperature` FLOAT(10) NOT NULL COMMENT 'Temperatura da sala [ºC].' ,
`Humidity` FLOAT(10) NOT NULL COMMENT 'Humidade relativa da sala [%].',
PRIMARY KEY (id)
)
ENGINE = InnoDB;
'''



# Modbus uitlezen
# Apparaat: DDS238-1 ZN (KWh meter)
#
# Script gemaakt door S. Ebeltjes (domoticx.nl)
from pymodbus.client.sync import ModbusSerialClient

'''
import pymodbus
from __future__ import division
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.constants import Endian              # Nodig voor 32-bit float getallen (2 registers / 4 bytes)
from pymodbus.payload import BinaryPayloadDecoder  # Nodig voor 32-bit float getallen (2 registers / 4 bytes)
from pymodbus.payload import BinaryPayloadBuilder  # Nodig om 32-bit floats te schrijven naar register
'''

import time
import MySQLdb
import os
import subprocess
import math

import sys
sys.path.append('/root/medidor/')
from DDS238_4W import *

class XYMD02:
    def __init__(
        self,
        DeviceAddress,
        client,
    ):
        self.DeviceAddress = DeviceAddress
        self.client = client
    
    def ReadTemp(self):
        
        address=0x0001
        count=1
        
        data = self.client.read_input_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/10.
    
    def ReadHumidity(self):
        
        address=0x0002
        count=1
        
        data = self.client.read_input_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]/10.
    
    def ReadDeviceAdress(self):
        
        address=0x0101
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]
    
    def ReadBaudRate(self):
        
        address=0x0102
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]
    
    def ReadTemperatureCorrection(self):
        
        address=0x0103
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]
        
    def ReadHumidityCorrection(self):
        
        address=0x0104
        count=1
        
        data = self.client.read_holding_registers(address=address, count=count, unit=self.DeviceAddress)
        if len(data.registers) > 1:
            return sum(data.registers)
        else:
            return data.registers[0]
        
    def WriteDeviceAdress(self):
        
        address=0x0101 # Adress of the register
        NewDeviceAddress=0x02 # New device address
        self.client.write_register(address = address, value = NewDeviceAddress, unit = self.DeviceAddress)

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)
    
    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

method = "rtu"
baudrate = 9600
stopbits = 1
bytesize = 8
parity = "N"
timeout = 1
retries = 2

port = ''
client = ModbusSerialClient()

while True:
    time.sleep(3)
   
    if not os.path.exists(port):
        for i in range(10):
            if os.path.exists('/dev/ttyUSB'+str(i)):
                port = ('/dev/ttyUSB'+str(i))
                break
   
    try:
        conn = MySQLdb.connect(
            host="10.0.1.13",    # your host, usually localhost
            user="iot",         # your username
            passwd="r:F*-Xs7X}eR6j8k3z$x@X*2<ju-nB{LxQ",  # your password
            db="iot",        # name of the data base
            connect_timeout=1
        )
        cursor = conn.cursor()
        sql_connected = True
    except:
        sql_connected = False
        print("Erro ao conectar no servidor mysql")
        continue
    
    if not client.is_socket_open():
        try:
            client = ModbusSerialClient(
                method = method,
                port = port,
                stopbits = stopbits,
                bytesize = bytesize,
                parity = parity,
                baudrate = baudrate,
                timeout = timeout,
                retries = retries
            )
            connection = client.connect()
            device01 = DDS238_4W(DeviceAddress = 0x01, client = client)
            device02 = XYMD02(DeviceAddress = 0x02, client = client)
        except:
            print("Modbus connectie error / DDS238-1 ZN")
            continue
    
    if client.is_socket_open() and sql_connected :
        #Date = int(time.time()) # epoch in seconds format
        Date = int(truncate(time.time(), 3)*1000) # epoch in miliseconds format
        
        try:
            TotalWork = device01.ReadTotal()
            Voltage = device01.ReadVoltage()
            Amperage = device01.ReadAmperage()
            ActivePower = device01.ReadActivePower()
            ReactivePower = device01.ReadReactivePower()
            PowerFactor = device01.ReadPowerFactor()
            Frequency = device01.ReadFrequency()
            
            sql = "INSERT INTO EnergyMeter (Time, MeterID, TotalWork, Voltage, Current, ActivePower, ReactivePower, PowerFactor, Frequency) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (Date, 1, TotalWork, Voltage, Amperage, ActivePower, ReactivePower, PowerFactor, Frequency))
            
            print(
                "****************"
                "\nConsumo Acumulado [KWh]: "+str(TotalWork)+
                "\nTensão [V]: "+str(Voltage)+
                "\nCorrente [A]: "+str(Amperage)+
                "\nPotencia Ativa [W]: "+str(ActivePower)+
                "\nPotencia Reativa [W]: "+str(ReactivePower)+
                "\nFator de Potência [º]: "+str(PowerFactor)+
                "\nFrequência [Hz]: "+str(Frequency)+
                "\n****************"
            )
        except:
            print("Erro ao obter os dados no sensor DDS238_4W.")
            pass
        
        time.sleep(1)
        try:
            RoomTemperature = device02.ReadTemp()
            RoomHumidity = device02.ReadHumidity()
            
            sql = "INSERT INTO HumidityMeter (Timestamp, MeterID, Temperature, Humidity) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (Date, 2, RoomTemperature, RoomHumidity))
            
            print(
                "****************"
                "\nTemperatura Ambiente [ºC]: "+str(RoomTemperature)+
                "\nHumidade Relativa [%]: "+str(RoomHumidity)+
                "\n****************"
            )
        except:
            print("Erro ao obter os dados no sensor XYMD02.")
            pass
        
        time.sleep(1)
        try:
            srv04Cpu0Temp, srv04Cpu0TempError = subprocess.Popen(['/bin/cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            srv04Cpu1Temp, srv04Cpu1TempError = subprocess.Popen(['/bin/cat', '/sys/class/thermal/thermal_zone1/temp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            #srv04Cpu0Temp = srv04Cpu0Temp.replace('\n', '')
            #srv04Cpu1Temp = srv04Cpu1Temp.replace('\n', '')

            srv03Cpu0Temp, srv03Cpu0TempError = subprocess.Popen(['ssh', 'srv03', '/bin/cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            srv03Cpu1Temp, srv03Cpu1TempError = subprocess.Popen(['ssh', 'srv03', '/bin/cat', '/sys/class/thermal/thermal_zone1/temp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            
            if not srv04Cpu1TempError:
                sql = "INSERT INTO Hardware (Timestamp, Name, Cpu0Temp, Cpu1Temp) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (Date, 'srv04', srv04Cpu0Temp, srv04Cpu1Temp))
                cursor.execute(sql, (Date, 'srv03', srv03Cpu0Temp, srv03Cpu1Temp))
            else:
                print("Erro ao obter as temperaturas dos CPUs.")
        except:
            print("Erro ao obter os dados de temperatura dos CPU's.")
            pass
        
        try:
            conn.commit()
            cursor.close()
            conn.close()
        except:
            print("Erro ao tentar inserir os dados na tabela.")
            continue











