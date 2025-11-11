# ------------------------------------------------------
# Secuencia programada UR3e - RoboDK
# ------------------------------------------------------
# Autor: [Joaquin Cisneros]
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


# Seleccionar robot por nombre
robot = RDK.Item('UR3e')
fresa= RDK.Item('FRESA')
foto = RDK.Item('FOTO_FRAME')
camara = RDK.Item('Frame 3')

robot.setSpeed(speed_linear=500, speed_joints=30) # restaura velocidad normal

# ------------------------------------------------------
# Definición inicial
# ------------------------------------------------------

Pos_foto = [-1.864511, -24.320595, -27.297083, -128.192464, 91.444518, 299.996035]
Pos_Approach_Fresa_in = [86.128271, 23.320939, -151.459881, 38.138942, 90.000000, 210.768710]
Pos_Approach_Caja =[60.152901, -39.811733, 7.133262, 117.955824, 90.295372, 183.570722]
Pos_Caja = [60.091010, -48.955721, 41.526286, 92.706472, 90.290276, 183.509040]
Pos_Mov_circular = [139.771499, -57.545059, 125.720491, -158.165584, 90.001738, -231.151499]

# ------------------------------------------------------
# Secuencia de movimientos
# ------------------------------------------------------

print("Iniciando secuencia programada...")

# 2. POS_FOTO: observación del entorno
print("→ POS_FOTO (Inspección)")
robot.MoveJ(Pos_foto)


while True:
    robot.setPoseFrame(foto)   # Base frame for movements
    # 2.1 Centrar fresa
    print("→ CENTRAR_FRESA")

    # Pose de la fresa respecto a la cámara (matriz 4x4)
    matrix_center = main()

    if matrix_center is None:
        print("No se detectó ninguna fresa.")
        break
    else:
        print("Fresa detectada")
        pass

    # (opcional) igualar Z a cero si quieres
    matrix_center[2,3] = 0

    # extraer tvec
    tvec = matrix_center[0:3, 3]

    # conservar la orientación actual del robot y solo cambiar la traslación
    current_pose = robot.Pose()                    # robomath.Mat
    target_pose = robomath.Mat(current_pose)      # copia
    target_pose[0,3] = float(tvec[0])
    target_pose[1,3] = float(tvec[1])
    target_pose[2,3] = float(tvec[2])

    print("Moviendo solo en traslación a:", tvec)
    robot.MoveJ(target_pose)

    # 3. POS_APPROACH_FRESA: acercamiento seguro
    print("→ POS_APPROACH_FRESA (acercamiento)")

    matrix = main()  # o matriz obtenida por visión

    # Crear frame temporal igual que el frame 3 para moverse respecto a el
    new_frame = RDK.AddFrame("temp_frame", RDK.Item("UR3e"))
    new_frame.setPose(camara.Pose())

    new_frame.setParentStatic(foto)

    robot.MoveJ(Pos_Approach_Fresa_in)

    robot.setPoseFrame(new_frame)   # Base frame for movements
    new_pose = robot.Pose() # copia
    new_target_pose = robomath.Mat(new_pose)      # copia
    new_target_pose[0,3] = float(matrix[0,3])
    new_target_pose[1,3] = float(matrix[1,3]+200)
    new_target_pose[2,3] = float(matrix[2,3]) 
    print("Moviendo solo en traslación a:", tvec)

    robot.MoveJ(new_target_pose)

    # 4. POS_FRESA: ascenso suave hacia la fresa
    print("→ POS_FRESA (ascenso hacia la fresa)")
    pose_fresa = robot.Pose() # copia
    pose_fresa = robomath.Mat(pose_fresa)      # copia
    pose_fresa[1,3] = float(pose_fresa[1,3] - 100)  # Sube 100 mm
    robot.MoveJ(pose_fresa)

    # Connect to Arduino
    arduino_comm.connect_arduino()

    # Open valve (send 1)
    arduino_comm.send_one()
    time.sleep(1)    # Esperar 1 segundo para asegurar la succión
    # Wait until Arduino prints "Listo"
    arduino_comm.wait_for_ready(timeout=120)



    #5. POS_POSTPICK: movimiento circular para evitar colisiones
    # pose_postpick = robot.Pose() # copia
    # pose_postpick = robomath.Mat(pose_postpick)      # copia
    # pose_postpick[1,3] = float(pose_postpick[1,3] + 100)  # Baja 100 mm
    # robot.MoveJ(pose_postpick)
    print("→ POS_POSTPICK (arranque de fresa)") 
    joints = robot.Joints()   # Convert to Python list
    print("Current joints:", joints)

    # Add +60 degrees to the first joint (index 0)
    joints[0] -= 60
    print("New joints:", joints)

    # Move robot to the new joint configuration
    robot.MoveJ(joints)

    #6. PLACE/DROP: movimiento hacia la caja
    print("→ PLACE/DROP (colocación de fresa)")

    robot.MoveJ(Pos_Approach_Caja)
    robot.MoveJ(Pos_Caja)
    # Close valve (send 0)
    arduino_comm.send_zero()

    time.sleep(3)    # Esperar 1 segundo para asegurar la suelta

    #7. Regresar a foto
    print("→ POS_FOTO (regreso a inspección)")

    robot.MoveJ(Pos_foto)
    remove_frame = RDK.Item("temp_frame")
    remove_frame.Delete()
    # Clean up
    time.sleep(2)
    arduino_comm.close_connection()