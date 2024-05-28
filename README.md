# Interaction Behaviours for Social Intelligence
**DA231X - Degree Project**
This repository consists of code for the interaction behaviours developed as part of an effort to make an autonomous lawnmower "socially intelligent". This degree project was conducted in collaboration with [Husqvarna]([url](https://www.husqvarna.com/se/)) who generously lent their HUSQVARNA AUTOMOWER® 550 EPOS research unit for testing and experiment purposes. For reference, ![The Husqvarna Lawnmower used](https://www-static-nw.husqvarna.com/-/images/aprimo/husqvarna/robotic-mowers/photos/studio/jj-494694.webp?v=26bf646d148fd9b9&format=WEBP_LANDSCAPE_CONTAIN_XXL)


## Interaction Behaviours
- The script in `ROS Packages` is used to build a, you guessed it, a `ROS Package`. Which is uploaded to the Lawnmower's onboard RaspberryPi.
- The script `serv.py` in `interactions` is uploaded to to the RaspberryPi, and run before launching the executable `enhanced_rd`.
- the Executable communicates with the server instance which controls the LED strip onboard. Different key combinations on the executable perform different interaction behaviours with the mower.

## Analysis
- The folder `User Study` contains the anonymized data and the analysis conducted on the data to drive insights into how social behaviours displayed by an autonomous mobile robot impacts its safety perception and trustworthiness by humans.
