Python Script to Control a Drone and Fly an Arbitrary Pattern Using WSL (Ubuntu)

This document provides step-by-step instructions to set up PX4 and JMAVSim on Windows Subsystem for Linux (WSL) with Ubuntu and execute a Python script to control a drone and fly an arbitrary pattern defined in a text file.

---

Prerequisites

 1. Install Windows Subsystem for Linux (WSL)
Ensure you have WSL installed and running with Ubuntu:

1. Open PowerShell as Administrator and run:
   
   wsl --install -d Ubuntu
   
2. Restart your machine if prompted.
3. Open Ubuntu Terminal and update packages:
   
   sudo apt update && sudo apt upgrade -y
   
2. Install Required Dependencies
PX4 requires several dependencies for simulation:
   
   sudo apt install -y python3 python3-pip git cmake build-essential \
       ninja-build exiftool g++-multilib autoconf automake \
       libtool ccache gdb valgrind \
       protobuf-compiler libeigen3-dev libopencv-dev \
       wget unzip xxd kmod openjdk-11-jdk
   
3. Install PX4 Toolchain
Clone the PX4 repository and install additional dependencies:
   
   git clone --recursive https://github.com/PX4/PX4-Autopilot.git
   cd PX4-Autopilot
   bash Tools/setup/ubuntu.sh
   
4. Setup OpenJDK-11 for JMAVSim
JMAVSim requires Java to run. Ensure OpenJDK-11 is installed inside the PX4-Autopilot directory:
   
   cd PX4-Autopilot
   sudo apt install -y openjdk-11-jdk
   
---

 Building and Running PX4 with JMAVSim

 1. Set Up Environment Variables
   
   export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:$HOME/PX4-Autopilot/build/px4_sitl_default/build_gazebo
   export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$HOME/PX4-Autopilot/Tools/sitl_gazebo/models
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/PX4-Autopilot/build/px4_sitl_default/build_gazebo
   export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:$HOME/PX4-Autopilot/Tools/sitl_gazebo
   
2. Build PX4 for SITL Simulation
   
   cd ~/PX4-Autopilot
   make px4_sitl jmavsim
   
This command compiles PX4 for Software-In-The-Loop (SITL) with JMAVSim as the simulator.

 3. Run JMAVSim
   
   make px4_sitl jmavsim
   
After execution, you should see a simulated drone taking off in a virtual environment.

---

 Running Your MAVSDK Code on WSL
To run your MAVSDK-based flight controller on WSL:

1. Navigate to the project directory containing `drone_controller.py`:
   
   cd ~/your_project_directory
   
2. Ensure MAVSDK is installed:
   
   pip3 install mavsdk
   
3. Start PX4 SITL in one terminal:
   
   cd ~/PX4-Autopilot
   make px4_sitl jmavsim
   
4. Open a new terminal and run your Python script:
   
   python3 drone_controller.py
   
---

Updating Waypoints in the Simulation
To modify the drone's flight path, update the `waypoints.txt` file:

1. Open `waypoints.txt` in a text editor:
   
   nano waypoints.txt
   
2. Add or modify waypoints in the format:
   
   latitude,longitude,altitude
   47.3977415,8.5455933,50
   47.3978425,8.5456800,50
   47.3979600,8.5458000,50
   
3. Save and exit (for nano, press `CTRL+X`, then `Y`, and `ENTER`).
4. Restart the MAVSDK script to apply the new waypoints:
   
   python3 drone_controller.py
   
---

Testing PX4 SITL with MAVSDK
To confirm that the drone is properly controlled via MAVSDK:

1. Open a separate terminal and run:
   
   cd PX4-Autopilot
   source Tools/setup_gazebo.bash $(pwd) $(pwd)/build/px4_sitl_default
   
2. Run a MAVSDK script (e.g., `drone_controller.py`):
   
   python3 drone_controller.py
   
---

 Troubleshooting

 1. PX4 Build Fails
- Ensure you have installed all dependencies correctly.
- Run the following to clean and rebuild:
   
   make clean
   make px4_sitl jmavsim
   
 2. JMAVSim Not Launching
- WSL does not natively support GUI applications. Use an X server like **VcXsrv** to display JMAVSim’s GUI.
- Install and launch **VcXsrv**, then run:
   
   export DISPLAY=:0
   make px4_sitl jmavsim
   
 3. MAVSDK Connection Issues
- Ensure PX4 is running and listening for MAVSDK connections.
- Check if MAVSDK is properly installed using:
   
   pip3 install mavsdk
   
---

 Next Steps
- Integrate PX4 with Gazebo for advanced simulations.
- Customize flight paths using `waypoints.txt`.
- Implement real-world tests on the Alta X drone.

This guide provides all the necessary steps to get PX4 and JMAVSim running on WSL. If you encounter any issues, refer to the PX4 documentation or the GitHub community for support.
