# :eye: Project Perceive :eye:
## Manufacturing data collectors stack.
Project Perceive is a full stack IoT platform to be used at manufacturing sites to collect machine data in the absence of SCADA and/or PLC's. The current state of the project is effectively, multi-input, wireless, remote I/O blocks; that is, 24V signals from PLC’s or stand-alone sensors are collected and sent back to a database for analysis. The aim is to provide production with performance figures and maintenance with availability figures (with the end goal to present full OEE data per machine). These would be available in the form of web page dashboards.

**Table of contents**
* [Project Scope](https://github.com/rvUnipart/ProjectPerceive/blob/master/README.md#project-scope)
* [Stack Architecture](https://github.com/rvUnipart/ProjectPerceive/blob/master/README.md#stack-architecture)
* [Contributions](https://github.com/rvUnipart/ProjectPerceive/blob/master/README.md#contributions)
* [FAQ](https://github.com/rvUnipart/ProjectPerceive/blob/master/README.md#faq)

# Project Scope
To protect against scope creep and ensure that Project Perceive doesn't overlap with other digital projects; all work undertaken must fall under the list of objectives below.
* Collect machine data from manufacturing sites (industrial setting).
* Provide machine independent solutions - genericized device interacting with bespoke machine sensors/signals.
* Be able to collect data from both digital and analog sensors/signals.
* Must not interfere with the normal operation of machines and must fail safe.
* Not to be used on machines where SCADA is present.
* Sensors/signals need to be chosen so that data yields a value to the company.
* Relevant data needs to be presented in real-time via a web-based format.

# Stack Architecture
The current/existing stack:
* Edge/field devices: custom firmware on [NodeMCU's](https://www.nodemcu.com/index_en.html) (ESP8266).
* Messaging protocol, edge devices to server: [MQTT](https://mqtt.org/).
* Messaging broker: [Mosquitto](https://mosquitto.org/).
* Messaging broker to database bridging: Python script.
* Database: [MySQL](https://www.mysql.com/).
* Server: Linux (Ubuntu) VM.
* Data visualisation: Apache serving PHP.

# Contributions
Project Perceive is a collaborative project within the Unipart Digital Champions network. Anyone at Unipart can [apply](https://www.unipartwayonline.com/systems-tools/digital/digital-community/) to be a Digital Champion meaning that anyone at Unipart can also get involved in Project Perceive.

The internal development log can be found [here](https://docs.google.com/document/d/107jLMQkJ1DhkErDfkK61GGhLysu-sKJysHNekaJKcYs/edit).

# FAQ
* Q: How is the project managed?
* A: The project will be run in an open source manner. There are no specific milestones or timing requirements for contributors.

* Q: Will I be required to visit particular sites to be able to contribute?
* A: On-site work is optional. Obviously if you would like to install devices or undertake mechanical design change work then you will need to be on-site for those pieces of work.
