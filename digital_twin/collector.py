# ------------------------------------------------------
# Secuencia programada UR3e - RoboDK
# ------------------------------------------------------
# Autor: [Joaquin Cisneros]
# Descripción: Simula el ciclo de inspección, toma y depósito de una fresa.
# ------------------------------------------------------

from robodk import robolink, robomath
from strawberry_recognition import main
RDK = robolink.Robolink()
RDK.setRunMode(robolink.RUNMODE_RUN_ROBOT)  # Modo simulación
import numpy as np

# Seleccionar robot por nombre
robot = RDK.Item('UR3e')
fresa= RDK.Item('FRESA')
foto = RDK.Item('FOTO_FRAME')
camara = RDK.Item('Frame 3')


robot.setSpeed(speed_linear=800, speed_joints=80) # restaura velocidad normal

# ------------------------------------------------------
# Definición inicial
# ------------------------------------------------------

Home = [90.000000, -90.000000, 90.000000, -90.000000, -90.000000, -0.000000]
Pos_foto = [-1.864511, -24.320595, -27.297083, -128.192464, 91.444518, 299.996035]
Pos_Approach_Fresa_out = [86.128271, 10.009225, -143.917990, 43.908765, 90.000000, 210.768710]
Pos_Approach_Fresa_in = [86.128271, 23.320939, -151.459881, 38.138942, 90.000000, 210.768710]
Pos_Approach_Caja = [42.874238, -72.243947, 39.183983, -56.940036, -90.000000, -47.125762]
Pos_Caja = [42.874238, -74.452121, 102.776276, -118.324155, -90.000000, -47.125762]
Pos_Mov_circular = [139.771499, -57.545059, 125.720491, -158.165584, 90.001738, -231.151499]
#Pose Inicial
print("→ POS_FOTO (Inspección)")
robot.MoveJ(Pos_foto)


# ------------------------------------------------------
# Calcular Fresa_abajo (Pos_Fresa bajada 200 mm en Z)
# ------------------------------------------------------

#pose_fresa_respecto_camara = fresa.Pose()

#pose_fresa_respecto_camara = main()  # o matriz obtenida por visión
#pose_fresa_respecto_camara = np_to_pose(pose_fresa_respecto_camara)
#print("Pose fresa respecto a cámara (mm):")
#print(pose_fresa_respecto_camara)



# ------------------------------------------------------
# Secuencia de movimientos
# ------------------------------------------------------

print("Iniciando secuencia programada...")

# 1. HOME: posición inicial segura
#print("→ HOME")
#robot.MoveJ(Home)

# 2. POS_FOTO: observación del entorno
print("→ POS_FOTO (Inspección)")
robot.MoveJ(Pos_foto)
robot.setPoseFrame(foto)   # Base frame for movements


# 2.1 Centrar fresa
print("→ CENTRAR_FRESA")

# Pose de la fresa respecto a la cámara (matriz 4x4)
matrix_center = main()

# (opcional) igualar Z a cero si quieres
matrix_center[2,3] = 0

# extraer tvec
tvec = matrix_center[0:3, 3]

# conservar la orientación actual del robot y solo cambiar la traslación
current_pose = robot.Pose()                    # robomath.Mat
target_pose = robomath.Mat(current_pose)      # copia
target_pose[0,3] = float(tvec[0])
target_pose[1,3] = float(tvec[1])

print("Moviendo solo en traslación a:", tvec)
robot.MoveJ(target_pose)

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

# #robot.MoveJ(Fresa_abajo)

# Fresa_abajo = robomath.Mat(matrix)  # Ajustar altura de agarre
# #Fresa_abajo = Fresa_abajo * robomath.transl(0,-40,-200)  # Baja 200 mm

# # 5. POS_FRESA: simula el agarre (sube suavemente)
# print("→ POS_FRESA (agarre de la fresa)")
# robot.MoveL(Fresa_abajo*robomath.transl(0,0,50))
# time.sleep(10)              # wait 2 seconds

# # 6. FRESA ABAJO (RETORNO): descenso rápido para soltar
# print("→ FRESA_ABAJO (retorno rápido)")
# robot.setSpeed(400)  # velocidad alta temporal
# robot.MoveL(Fresa_abajo)

# #6.5. MOVIMENTO PARA ARRANCAR:
# #print("→ MOVIMENTO PARA ARRANCAR")
# #robot.setSpeed(400)  # velocidad alta temporal
# #Joints = robot.Joints()
# #Joints_memoria= Joints
# #print(Joints)

# #Joints[-1]=  -360
# #robot.MoveJ(Joints)
# #print(Joints)

# #Joints[-1]=  360
# #robot.MoveJ(Joints)
# #print(Joints)

# #robot.MoveJ(Joints_memoria)
# robot.setSpeed(100)  # restaura velocidad normal

# # 7. POS_APPROACH_FRESA: retirada segura
# print("→ POS_APPROACH_FRESA (retirada)")
# robot.MoveJ(Pos_Approach_Fresa_out)

# # 8. POS_APPROACH_CAJA: moverse hacia el área de depósito
# print("→ POS_APPROACH_CAJA")
# robot.MoveJ(Pos_Approach_Caja)

# # 9. POS_CAJA: colocar la fresa
# print("→ POS_CAJA (liberación)")
# robot.MoveL(Pos_Caja)

# # 10. POS_APPROACH_CAJA: moverse hacia el área de depósito
# print("→ POS_APPROACH_CAJA (retirada)")
# robot.MoveL(Pos_Approach_Caja)


# # 11. POS_FOTO: regreso al punto de observación
# print("→ POS_FOTO (fin del ciclo)")
# robot.MoveJ(Pos_foto)

# print("Secuencia finalizada correctamente.")