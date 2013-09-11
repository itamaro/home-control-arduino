home-control-arduino
====================

Arduino projects for my home control system.

Arduino IR Receiver / Analyser
------------------------------

Using this circuit: ![Arduino PhotoTransistor Circuit](docs/Arduino-PhotoTransistor-Circuit.jpg),

and loading the [IRACreceiver](IRACreceiver) project to the Arduino,
the Arduino will print to serial raw data on received IR signals, in the form:
> 0x12345678 (32 bits)
> Raw (182): -27866 3050 -3650 2100 -850 1100 -1800 1050 -800 1150 -800 2050 -850 ...

The HEX value is the decoded signal value,
and the raw list is a list of IR marks (positive numbers) and spaces (negative numbers) in microseconds -
as explained in the [Ken Shirriff's library page](http://www.righto.com/2009/08/multi-protocol-infrared-remote-library.html).

