# Small-Scale Wind Energy Activity

![Turbine CAD Rendering](/ImagesforReadmeWiki/WindTurbineRender.png)

## Overview

This activity was developed to introduce students to wind energy and blade design. In terms of hardware, this project consists of a wind turbine upright and hub. The hub has a 1/4" drive shaft to allow students to fasten their blade and hub assemblies. Assemblies are held in place by tightening a wingnut against them. The driveshaft leads to a pulley drive which provides a 4:1 speed increase going into a DC motor. When spun, the DC motor creates a voltage. This voltage is not expected to be more than 1.5 V.

The voltage from the DC motor is read by a microcontroller. Most microcontrollers only accepts positive voltages. If the motor is not spinning in the correct direction (creating a negative voltage), the microcontroller will not read any voltage. Flip the blade assembly over and try again.

The microcontroller is required to be plugged into a computer to operate. Voltage is displayed on an integrated LCD screen and is sent to the computer serially through whatever COM port the microcontroller is attached to. A data acquiistion and plotting package is provided to read and plot data collected by the microcontroller.

## Important Links

All source code, 3D STL models for printing, and guide images are provided in this main branch of the repository. 

For a single-file executable for the acquisition package which does not require downloading any dependancies, please see the [release section]https://github.com/DCHartlen/WindEnergyActivity/releases) of this repository.

For instructions on how build a turbine (including a suggested parts list), descripton of the microcontroller source code, and instruction on how to use the data Acquisiton package, please refer to [the project's wiki](https://github.com/DCHartlen/WindEnergyActivity/wiki).

## Credit
Project and source code was developed by Devon C. Hartlen for Engineers Nova Scotia.

## License
Source code is distributed under the MIT License. Anyone is free to do anything to the code so long as the original copyright is maintained. The developer does not hold any liability.
