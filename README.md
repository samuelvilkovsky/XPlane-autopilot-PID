
# Python Autopilot Controller for X-Plane

This project, developed by students at FEI TUKE, implements a Python-based Autopilot Controller utilizing a Proportional-Integral-Derivative (PID) algorithm to control aircraft within the X-Plane flight simulator. Leveraging the X-Plane Connect plugin, our solution facilitates real-time command and control of aircraft dynamics, offering a practical and educational tool for understanding the principles of automated flight systems. The project not only demonstrates the application of PID controllers in aviation but also provides a foundation for further exploration and enhancement in the realm of simulated flight control systems.



## Features

- **Real-time Aircraft Control:** Directly manipulate desired speed, altitude, and heading.
- **Integration with X-Plane Connect:** Seamless communication with the X-Plane environment.
- **Simple Web User Interface:** Control the autopilot via local running interface.


## Getting Started

To begin using this autopilot controller, please follow the installation and setup instructions.

&nbsp;1.  Install [Git](https://git-scm.com) to your device

&nbsp;2.  Download [X-Plane](https://x-plane.com) and [X-Plane Connect](https://github.com/nasa/XPlaneConnect). Install them according to their installation guides.

&nbsp;3.  Clone the project. Into the *[XPlaneLoc]/Resources/plugins/XPlaneConnect/Python3/*

```bash
git clone https://github.com/samuelvilkovsky/XPlane-autopilot-PID.git
```
&nbsp;4.  Install all required modules & libraries. (Make sure you have Python3 installed.)
```bash
pip install flask flask-socketio redis numpy pandas pyqtgraph gym
```
&nbsp;5.  Start XPlane and verify if your X-Plane Connect plugin is up & working.

&nbsp;6.  Run the *fl_script.py* file.
```bash
python fl_script.py
```

&nbsp;7.  Open port *http://127.0.0.1:5000* in your web browser.

&nbsp;7.  Start flight simulation in XPlane, takeoff and run the *PID_Autopilot.py* file.
```bash
python PID_Autopilot.py
```
## Contributing

Interested in contributing to the Python Autopilot Controller project? Here's how you can contribute:

&nbsp;1.  **Fork the Repository:** Click on the 'Fork' button at the top of the repository to create a copy of our project to your GitHub account.

&nbsp;2.  **Create a Branch:** Create a branch in your forked repository.

&nbsp;3.  **Make Your Changes:** Make modifications or additions to the project. Be sure to test your changes.

&nbsp;4.  **Submit a Pull Request:** Push your changes to your fork and then submit a pull request to our project. Provide a detailed description of what your changes are and why they should be included.
## License

MIT License

Copyright (c) *2024 Samuel Vilkovsky, Varvara Cherniavska, Lina Iliaschenko, David Spontak*

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

