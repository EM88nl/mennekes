from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import minimalmodbus

app = FastAPI()

instrument = minimalmodbus.Instrument('/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0', 50)
instrument.serial.baudrate = 57600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 2
instrument.serial.timeout = 1

class Configuration(BaseModel):
    """
    Represents the configuration settings for the application.

    Attributes:
        external_charging_current_limitation (float, optional): The external charging current limitation in Amperes per phase.
    """
    external_charging_current_limitation: Optional[float] = None

class Functions(BaseModel):
    """
    Represents the functions settings for the application.

    Attributes:
        master_heartbeat (int, optional): Master heartbeat is signalized with a pattern of 0x55AA.
        solar_charge_mode (int, optional): The solar charge mode, 0 = not supported, 1 = normal charging, 2 = sunshine mode, 4 = sunshine+ mode.
        req_phase_usage (int, optional): The required phase usage, not working at the moment.
        charging_release (int, optional): The charging release, 0 = not not allowed, 1 = chanrging released.
        lockmode (int, optional): The lock mode, 0 = not locked, 1 = locked (charging not possible).
    """
    master_heartbeat: Optional[int] = None
    solar_charge_mode: Optional[int] = None
    req_phase_usage: Optional[int] = None
    charging_release: Optional[int] = None
    lockmode: Optional[int] = None

def read_register(address, number_of_registers=1):
    """
    Helper function to read a register from the EVSE.

    Args:
        address (int): The address of the register to read.
        number_of_registers (int, optional): The number of registers to read. Defaults to 1.

    Raises:
        HTTPException: If an error occurs during the read operation.

    Returns:
        int: The value of the register.
    """
    if number_of_registers == 1:
        try:
            return instrument.read_register(address)
        except minimalmodbus.ModbusException as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        try:
            return instrument.read_long(address, number_of_registers=number_of_registers)
        except minimalmodbus.ModbusException as e:
            raise HTTPException(status_code=500, detail=str(e))
    
def read_string(address, length):
    """
    Helper function to read a string from the EVSE.

    Args:
        address (int): The address of the string to read.
        length (int): The length of the string.
    
    Raises:
        HTTPException: If an error occurs during the read operation.

    Returns:
        str: The value of the string.
    """
    try:
        return instrument.read_string(address, length)
    except minimalmodbus.ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def read_float(address):
    """
    Helper function to read a float from the EVSE.

    Args:
        address (int): The address of the float to read.

    Raises:
        HTTPException: If an error occurs during the read operation.
    
    Returns:
        float: The value of the float.
    """
    try:
        return instrument.read_float(address)
    except minimalmodbus.ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))

def write_register(address, value):
    """
    Helper function to write a register to the EVSE.

    Args:
        address (int): The address of the register to write.
        value (int): The value to write.

    Raises:
        HTTPException: If an error occurs during the write operation.
    """
    try:
        instrument.write_register(address, value)
    except minimalmodbus.ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def write_float(address, value):
    """
    Helper function to write a float to the EVSE.

    Args:
        address (int): The address of the float to write.
        value (float): The value to write.

    Raises:
        HTTPException: If an error occurs during the write operation.
    """
    try:
        instrument.write_float(address, value)
    except minimalmodbus.ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/version_info")
async def get_version_info():
    """Get version information of the EVSE."""
    return {
        "layout_version": read_register(0x0000),
        "firmware_version": read_string(0x0001, 8),
        "serial_number": read_string(0x0009, 8),
        "hw_version": read_register(0x0011),
        "product_id": read_register(0x0012)
    }

@app.get("/api/status")
async def get_status():
    """Get current status of the EVSE."""
    return {
        "evse_state": read_register(0x0100),
        "external_charging_release_state": read_register(0x0101),
        "external_downgrading_state": read_register(0x0102),
        "phase_rotation": read_register(0x0103),
        "bootup_token": read_register(0x0104, 2)
    }

@app.get("/api/configuration")
async def get_configuration():
    """Get current configuration of the EVSE."""
    return {
        "external_downgrading_current": read_float(0x0300),
        "external_charging_current_limitation": read_float(0x0302),
        "max_current_evse_group": read_float(0x0304),
        "max_current_evse": read_float(0x0306),
        "selective_phase_switching_option": read_register(0x030A)
    }

@app.post("/api/configuration")
async def set_configuration(config: Configuration):
    """Update configuration of the EVSE."""
    if config.external_charging_current_limitation is not None:
        write_float(0x0302, config.external_charging_current_limitation)
    return {"status": "Configuration updated"}

@app.get("/api/output_measurements")
async def get_output_measurements():
    """Get current output measurements."""
    return {
        "current_l1": read_float(0x0500),
        "current_l2": read_float(0x0502),
        "current_l3": read_float(0x0504),
        "voltage_l1": read_float(0x0506),
        "voltage_l2": read_float(0x0508),
        "voltage_l3": read_float(0x050A),
        "power_l1": read_float(0x050C),
        "power_l2": read_float(0x050E),
        "power_l3": read_float(0x0510),
        "power_overall": read_float(0x0512)
    }

@app.get("/api/charging_session")
async def get_charging_session():
    """Get current charging session information."""
    return {
        "max_session_charging_current": read_float(0x0B00),
        "session_charging_energy": read_float(0x0B02),
        "session_duration": read_register(0x0B04, 2)
    }

@app.get("/api/functions")
async def get_functions():
    """Get current functions of the EVSE."""
    return {
        "solar_charge_mode": read_register(0x0D03),
        "req_phase_usage": read_register(0x0D04),
        "charging_release": read_register(0x0D05),
        "lockmode": read_register(0x0D06)
    }

@app.post("/api/functions")
async def set_functions(func: Functions):
    """Update functions of the EVSE."""
    if func.master_heartbeat is not None:
        write_register(0x0D00, func.master_heartbeat)
    if func.solar_charge_mode is not None:
        write_register(0x0D03, func.solar_charge_mode)
    if func.req_phase_usage is not None:
        write_register(0x0D04, func.req_phase_usage)
    if func.charging_release is not None:
        write_register(0x0D05, func.charging_release)
    if func.lockmode is not None:
        write_register(0x0D06, func.lockmode)
    return {"status": "Functions updated"}

@app.get("/api/diagnostic")
async def get_diagnostic():
    """Get diagnostic information of the EVSE."""
    return {
        "last_error_code": read_register(0x0E00, 2)
    }