# ------------------------------------------------------
# Secuencia programada UR3e - RoboDK
# ------------------------------------------------------
# Autor: [Daniel De Regules & Joaquin Cisneros]
# Descripción: Simula el ciclo de inspección, toma y depósito de una fresa.
# ------------------------------------------------------

import sys
from robodk import robolink, robomath
from strawberry_recognition import main
RDK = robolink.Robolink()
RDK.setRunMode(robolink.RUNMODE_RUN_ROBOT)  # Modo simulación
import numpy as np
import time
import arduino_comm


# Global variables declaration
robot = RDK.Item('UR3e')
fresa= RDK.Item('FRESA')
foto = RDK.Item('FOTO_FRAME')
camara = RDK.Item('Frame 3')

robot.setSpeed(speed_linear=700, speed_joints=50) # restore normal speed

# ------------------------------------------------------
# Initial definition
# ------------------------------------------------------

Pos_foto = [-1.860000, -24.320000, -27.300000, -128.190000, 91.440000, 60.000000]
Pos_Approach_Fresa_in = [86.120000, 23.320000, -151.450000, 38.130000, 90.000000, -30.000000]
Pos_Approach_Caja =[60.150000, -39.810000, 7.130000, 117.950000, 90.290000, 210.000000]
Pos_Caja = [60.091010, -48.955721, 41.526286, 92.706472, 90.290276, 210.000000]
Pos_Home = [90.000000, -90.000000, 90.000000, -90.000000, -90.000000, 300.000000]
Out_range = [10.090000, -15.960000, -59.250000, -108.330000, 66.460000, 60.000000]

# ------------------------------------------------------
# Sequence of movements
# ------------------------------------------------------

print("Starting programmed sequence...")

# 1. POS_FOTO: environment observation
print("→ POS_FOTO (Inspection position)")
robot.MoveJ(Pos_foto)

# Infinite loop of inspection and collection
while True:
    robot.setPoseFrame(foto) 

    # Center strawberry
    print("→ CENTER_STRAWBERRY")
    # Pose of the strawberry relative to the camera (4x4 matrix)
    matrix_center = main(second_iteration=False)

    if matrix_center is None:
        print("No ripe strawberry detected.")
        break
    else:
        print("Strawberry detected, proceeding to pick.")
        pass

    tvec = matrix_center[0:3, 3]

    # Preserve the current orientation of the robot and only change the translation
    current_pose = robot.Pose()                    
    target_pose = robomath.Mat(current_pose)     
    # Offset to center the RGB Camera over the strawberry 
    target_pose[0,3] = float(tvec[0]) + 30 
    target_pose[1,3] = float(tvec[1]) + 100 
    target_pose[2,3] = float(tvec[2]) - 100 

    print("Moving only in translation to:", tvec)

    try:
        robot.MoveJ(target_pose)
    except Exception as e:
        robot.MoveJ(Out_range)

    # 3. POS_APPROACH_FRESA: Approach the strawberry
    print("→ POS_APPROACH_FRESA (approach)")

    matrix = main(second_iteration=True)

    if matrix is None:
        print("No ripe strawberry detected in second iteration.")
        robot.MoveJ(Pos_foto)
        continue
    
    # Create temporary frame same as frame 3 to move relative to it
    new_frame = RDK.AddFrame("temp_frame", RDK.Item("UR3e"))
    new_frame.setPose(camara.Pose())
    new_frame.setParentStatic(foto)

    # Move to approach position
    robot.MoveJ(Pos_Approach_Fresa_in)

    # Set robot reference frame to the new temporary frame
    robot.setPoseFrame(new_frame) 

    new_pose = robot.Pose()
    new_target_pose = robomath.Mat(new_pose)     
    new_target_pose[0,3] = float(matrix[0,3])
    new_target_pose[1,3] = float(matrix[1,3]+200)
    new_target_pose[2,3] = float(matrix[2,3]) 
    print("Moving only in translation to:", tvec)

    robot.MoveJ(new_target_pose)

    # 4. POS_FRESA: smooth ascent towards the strawberry
    print("→ POS_FRESA (smooth ascent towards the strawberry)")
    pose_fresa = robot.Pose() 
    pose_fresa = robomath.Mat(pose_fresa)      
    pose_fresa[1,3] = float(pose_fresa[1,3] - 153)  
    robot.MoveJ(pose_fresa)

    # Connect to Arduino
    arduino_comm.connect_arduino()

    # Open valve only if strawberry detected by Arduino (send 1)
    ready0 = False
    ready0 = arduino_comm.wait_for_fresa_si(timeout=7)
    if not ready0:
        print("No confirmation received for ready strawberry. Aborting cycle.")
        robot.MoveJ(Pos_Approach_Fresa_in)
        robot.MoveJ(Pos_foto)
        arduino_comm.send_zero()
        arduino_comm.close_connection()
        continue

    elif ready0:
        arduino_comm.send_one()
        print("Valve opened.")
    
    time.sleep(1)

    # Wait until Arduino prints "Listo"
    ready = False
    ready=arduino_comm.wait_for_ready(timeout=7)
    if not ready:
        print("No confirmation received for suction. Aborting cycle.")
        arduino_comm.send_zero()
        robot.MoveJ(Pos_Approach_Fresa_in)
        robot.MoveJ(Pos_foto)
        time.sleep(2)    # Wait 1 second to ensure release
        arduino_comm.close_connection()
        continue

    #5. POS_POSTPICK: after picking the strawberry
    print("→ POS_POSTPICK (after picking the strawberry)") 
    joints = robot.Joints()   # Convert to Python list
    print("Current joints:", joints)

    # Move -30 in z 
    post_pick_pose = robot.Pose() 
    post_pick_pose = robomath.Mat(post_pick_pose)      
    post_pick_pose[1,3] = float(post_pick_pose[1,3] + 50)
    post_pick_pose[2,3] = float(post_pick_pose[2,3] - 100)
    robot.MoveJ(post_pick_pose)

    # Add +60 degrees to the first joint (index 0)
    joints[0] -= 60
    print("New joints:", joints)

    # Move robot to the new joint configuration
    robot.MoveJ(joints)

    #6. PLACE/DROP: movement towards the box
    print("→ PLACE/DROP (placing the strawberry in the box)")

    robot.MoveJ(Pos_Approach_Caja)
    robot.MoveJ(Pos_Caja)
    arduino_comm.send_zero()

    # Wait 2 second to ensure release
    time.sleep(2)    

    # Small shaking movement to ensure the strawberry has been released
    robot.setSpeed(speed_linear=1400, speed_joints=100) 
    robot.setAcceleration(10000)  

    for i in range(2):
        joints = robot.Joints()  
        joints[4] -= 10
        joints[5] -= 30
        robot.MoveJ(joints)
        joints[4] += 10
        joints[5] += 30
        robot.MoveJ(joints)
        joints[4] -= 10
        joints[5] -= 30
        robot.MoveJ(joints)
        joints[4] += 10
        joints[5] += 30
        robot.MoveJ(joints)
    
    robot.setSpeed(speed_linear=700, speed_joints=50) # restore normal speed

    robot.MoveJ(Pos_Approach_Caja)

    #7. RETURN TO PHOTO POSITION
    print("→ POS_FOTO (return to inspection position)")

    robot.MoveJ(Pos_foto)
    remove_frame = RDK.Item("temp_frame")
    remove_frame.Delete()
    
    # Clean up
    time.sleep(2)
    arduino_comm.close_connection()