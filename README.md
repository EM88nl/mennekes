# Mennekes AMTRON® Compact 2.0S RESTful API

This project provides a RESTful API interface for interacting with the Mennekes AMTRON® Compact 2.0S, an electric vehicle charging station. The API allows for seamless integration and control of the charging station's functionalities, enabling developers to build custom applications or integrate with existing systems.

## RS-485 Interface

The Mennekes EV charger has a RS-485 interface that can be used to communicate with the device. This project provides a RESTful API that acts as a bridge between the charging station and external applications. The API allows you to perform various operations such as starting and stopping charging, getting the current status of the charging station, and control the allowed charging power. To use this API, you need to have a your charging station connected to a RS-485 to USB adapter and the adapter connected to your server.

### Setup Modbus RTU in the Mennekes AMTRON® Compact 2.0S

To enable the RS-485 interface in the Mennekes AMTRON® Compact 2.0S, you need to configure the Modbus RTU settings in the device. Follow the instructtions from the user manual. It is important to configure that you want to use the Modbus RTU interface for energy management in stead of for the energy meter.

## Installation

This API is implemented in Python using the FastAPI framework. To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

To start the API server, run the following command:

```bash
uvicorn main:app --reload
```

## Configuration

The API server reads the configuration from a file named `config.json`. The configuration file should contain the following fields:

```json
{
    "serial_port": "/dev/ttyUSB0", // Serial port of the RS-485 to USB adapter
    "address": 1, // Modbus address of the charging station
}
```

## Contributing

Contributions are welcome! Please fork the repository, create a new branch for your feature or bug fix, and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
