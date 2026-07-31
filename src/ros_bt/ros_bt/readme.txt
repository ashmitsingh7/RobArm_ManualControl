final

esp_read_enc2a.py uses rfcomm, same has to be used for esp_read_2b.py, merger remains the same mostly but make it a 7 angle array not 6----done

ros_write_motors.py also uses rfcomm but rn it considers 6 motors on one esp, need to change that to 3+3----done

multi_enc_isr_bt.cpp sends enc values----old
motors1.cpp receives actuation values=----old


where does limit switch and homing code go?----esp1

finally i think

1 cpp code for esp1(3enc+3motors), 1 cpp code for esp2(4 enc+3 motors)-----done

1 ros node to send and recieve values to esp1, 1 ros node to send and receive values to esp2------done
esp1 has limit switch code----done

thrn setup launch files to run all nodes and bind rfcomms-----to do

take into concern gear ratio for angles---done in isr code

check setup.py in the end to see if all nodes are mentioned----done

check pin numbers-3 enc to the 3 working ones, 2 enc to 2 working ones + as5600 to where the 2 limit switches were supposed to be----done in final esp codes

add a stop character to the control_node----done

change or make a new node isntead of control_node to make wrist and base move properly and not be individually actuated----done


1. splitting motor commands to 2 esps


ESP-A (rfcomm0) ----Local motor IDs 0–2
0 → gripper
1 → wrist1
2 → wrist2

ESP-B (rfcomm1)----Local motor IDs 0–2
0 → elbow
1 → shoulder / tt1
2 → shoulder / tt2

what does not change:
motors1.cpp(not yet)
MotorControl.msg
Joints.msg
control_node.py

what changes?
ros_write_motors.py 

ros_write_motors_espA.py   → rfcomm0 (gripper + wrists)
ros_write_motors_espB.py   → rfcomm1 (elbow + shoulders)

both motors subscribe to /motor_commands and pick different Joints

eg ros will send [0, 1, 255], esp serial will show M0: FWD PWM=255


espA_motors.cpp and espB_motors.cpp recieve values for their respective motors

all motor related codes:
ros_write_motors_espA.py
ros_write_motors_espB.py
MotorControl.msg
Joints.msg
control_node.py
espA_motors.cpp
espB_motors.cpp


2. adding encoder values
ESP-A (gripper + wrists ESP)----3 encoders total

enc0 → Wrist1  (magn quadrature)
enc1 → Wrist2  (magn quadrature)
enc2 → AS5600  (mounted at elbow)

ESP-B (elbow + shoulders ESP)------4 encoders total

enc0 → Elbow        (optical quadrature)
enc1 → Shoulder1   (magnetic quadrature)
enc2 → Shoulder2   (optical quadrature)
enc3 → AS5600


espA_encoders.cpp 
espB_encoders.cpp
espA_read_enc.py
espB_read_enc.py
esp_read_enc_merger.py

expected output [12.3, -4.5, 90.1, 180.0, 22.4, -10.2, 91.7] smthn like this


3. merge encoder and motor cpp codes


espA MAPPING

motor 0 → Gripper
motor 1 → Wrist1
motor 2 → Wrist2
angles[0] → Wrist1   (MAGNETIC)
angles[1] → Wrist2   (MAGNETIC)
angles[2] → Elbow    (OPTICAL)



ESPB MAPPING
motor 0 → Elbow
motor 1 → Shoulder 1
motor 2 → Shoulder 2
angles[0] → Elbow        (AS5600)
angles[1] → Shoulder 1  (MAGNETIC)
angles[2] → Shoulder 2  (OPTICAL)
angles[3] → Shoulder    (AS5600)

espA_motors_encoders.cpp
espB_motors_encoders.cpp

espA_read_enc.py
espB_read_enc.py
esp_read_enc_merger.py
ros_write_motors_espA.py
ros_write_motors_espB.py
MotorControl.msg
Joints.msg
control_node.py
the nodes dont change at all


youll be able to see a 3 or 4 angle array respectively

4. control_node.py had to be changed along with joints.msg for the new arm
a stop command was added which is x

    'r': ('gripper', 1),
    'f': ('gripper', 0),
    't': ('wrist1', 1),
    'g': ('wrist1', 0),
    'y': ('wrist2', 1),
    'h': ('wrist2', 0),
    'u': ('elbow', 1),
    'j': ('elbow', 0),
    'i': ('shoulder1', 1),
    'k': ('shoulder1', 0),
    'o': ('shoulder2', 1),
    'l': ('shoulder2', 0),
    stop all command-x

5. make a node instead of control_node to accomodate the different motions of the arm

Shoulder DOF 1 (pitch)
Shoulder DOF 2 (roll)
Elbow DOF
Wrist DOF 1 (pitch)
Wrist DOF 2 (roll)

node : control_node_v2.py

'r': [('gripper', +1)],  # open
'f': [('gripper', -1)],  # close
't': [('wrist1', -1), ('wrist2', +1)],  # pitch up
'g': [('wrist1', +1), ('wrist2', -1)],  # pitch down
'y': [('wrist1', +1), ('wrist2', +1)],  # roll ACW
'h': [('wrist1', -1), ('wrist2', -1)],  # roll CW
'u': [('shoulder1', -1), ('shoulder2', +1)],  # pitch up
'j': [('shoulder1', +1), ('shoulder2', -1)],  # pitch down
'i': [('shoulder1', +1), ('shoulder2', +1)],  # roll ACW
'k': [('shoulder1', -1), ('shoulder2', -1)],  # roll CW


5. limit switches and homing

add one ros command for this somwehre

rn doesnt autohome on boot bc we havent attached limit switches yet and have to test
add later i think

wrist 1 is the reference

home key=p

 

Check all which apply:

1. If I hit up limit switch on starting and send 0xff, it'll home and set wrist 1 encoder to 0

2. If I hit up limit switch in the middle during runtime but send 0xff, it'll home and do the same

3. If it hits up limit switch during runtime and doesn't get 0xff, it'll move down a little bit and encoder value doesn't get set to 0, it stops wrist motors and waits for commands

4. If it hits down limit switch during or runtime and does or does not get 0xff, it'll move up a little bit and encoder value does not get set to 0, it stops wrist motors and waits for commands

5. it cant go down without going up at the beginning, forces you to home so ive commented out one line for now



home key=p



NODES TO KEEP AND ADD TO SETUP.py

in controls:
control_node_v2.py

'control_node_v2 = controls.control_node_v2:main',

custom_msg:
this has no setup.py so idk if its a ros2 pkg

ros_bt:
esp_read_enc_merger.py
espA_read_enc.py
espB_read_enc.py
ros_write_motors_espA.py
ros_write_motors_espB.py


'esp_read_enc_merger = ros_bt.esp_read_enc_merger:main',
'espA_read_enc= ros_bt.espA_read_enc:main',
'espB_read_enc= ros_bt.espA_read_enc:main',
'ros_write_motors_espA=ros_bt.ros_write_motors_espA:main',
'ros_write_motors_espB=ros_bt.ros_write_motors_espB:main',

espA_motors_encoders.cpp
espB_motors_encoders.cpp
these 2 go on the esps





























