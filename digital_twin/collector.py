# ------------------------------------------------------
# Secuencia programada UR3e - RoboDK
# ------------------------------------------------------
# Autor: [Joaquin Cisneros]
# Descripción: Simula el ciclo de inspección, toma y depósito de una fresa.
# ------------------------------------------------------

from robodk import robolink, robomath
RDK = robolink.Robolink()
import time
# Seleccionar robot por nombre
robot = RDK.Item('UR3e')
fresa= RDK.Item('FRESA')
camara = RDK.Item('Frame 3')

# ------------------------------------------------------
# Definición inicial
# ------------------------------------------------------

Home = [90.000000, -90.000000, 90.000000, -90.000000, -90.000000, -0.000000]
Pos_foto = [-3.060000, -94.717200, 87.920000, -173.012800, 92.640000, 300.000000]
Pos_Approach_Fresa_out = [45.907130, -92.313172, 92.259841, -89.946669, 90.000000, 177]
Pos_Approach_Fresa_in = [90.632897, -61.130997, 125.946568, -154.815570, 90.000000, 176.569122]
Pos_Approach_Caja = [42.874238, -72.243947, 39.183983, -56.940036, -90.000000, -47.125762]
Pos_Caja = [42.874238, -74.452121, 102.776276, -118.324155, -90.000000, -47.125762]
Pos_Mov_circular = [139.771499, -57.545059, 125.720491, -158.165584, 90.001738, -231.151499]
#Pose Inicial
print("→ POS_FOTO (Inspección)")
robot.MoveJ(Pos_foto)


# ------------------------------------------------------
# Calcular Fresa_abajo (Pos_Fresa bajada 200 mm en Z)
# ------------------------------------------------------

pose_fresa_respecto_camara = fresa.Pose()
print('pose_fresa_respecto_camara')
print(pose_fresa_respecto_camara)

pose_camara_respecto_flange = camara.Pose()  # o matriz conocida/calibrada
print('pose_camara_respecto_flange')
print(pose_camara_respecto_flange)

pose_camara_respecto_robot = robot.Pose()
print('pose_camara_respecto_robot')
print(pose_camara_respecto_robot)


# Pose de la fresa con respecto al robot
pose_fresa = pose_camara_respecto_robot *pose_camara_respecto_flange* pose_fresa_respecto_camara
print("Pose de la fresa respecto al robot:")
print(pose_fresa)

print(pose_fresa.Pos())

xyz_fresa = pose_fresa.Pos()                     # <-- correct
pose_fresa_trans = robomath.transl(xyz_fresa)   # rebuild pure translation pose
print("Pose fresa (translation only):")
print(pose_fresa_trans)


# Mover la fresa 200 mm hacia abajo (en su propio eje Z)
Fresa_abajo = pose_fresa_trans * robomath.transl(0, 0, -200)*robomath.rotz(300)
print('Fresa_abajo')
print(Fresa_abajo)

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

# 3. APPROACH FRESA: acercamiento a la fresa
print("→ POS_APPROACH_FRESA")
robot.MoveJ(Pos_Approach_Fresa_in)

# 4. FRESA ABAJO: movimiento de aproximación suave
print("→ FRESA_ABAJO (baja suavemente)")
robot.MoveJ(Fresa_abajo)

# 5. POS_FRESA: simula el agarre (sube suavemente)
print("→ POS_FRESA (agarre de la fresa)")
robot.MoveL(Fresa_abajo*robomath.transl(0,0,50))
time.sleep(2)              # wait 2 seconds

# 6. FRESA ABAJO (RETORNO): descenso rápido para soltar
print("→ FRESA_ABAJO (retorno rápido)")
robot.setSpeed(400)  # velocidad alta temporal
robot.MoveL(Fresa_abajo)

#6.5. MOVIMENTO PARA ARRANCAR:
#print("→ MOVIMENTO PARA ARRANCAR")
#robot.setSpeed(400)  # velocidad alta temporal
#Joints = robot.Joints()
#Joints_memoria= Joints
#print(Joints)

#Joints[-1]=  -360
#robot.MoveJ(Joints)
#print(Joints)

#Joints[-1]=  360
#robot.MoveJ(Joints)
#print(Joints)

#robot.MoveJ(Joints_memoria)
robot.setSpeed(100)  # restaura velocidad normal

# 7. POS_APPROACH_FRESA: retirada segura
print("→ POS_APPROACH_FRESA (retirada)")
robot.MoveJ(Pos_Approach_Fresa_out)

# 8. POS_APPROACH_CAJA: moverse hacia el área de depósito
print("→ POS_APPROACH_CAJA")
robot.MoveJ(Pos_Approach_Caja)

# 9. POS_CAJA: colocar la fresa
print("→ POS_CAJA (liberación)")
robot.MoveL(Pos_Caja)

# 10. POS_APPROACH_CAJA: moverse hacia el área de depósito
print("→ POS_APPROACH_CAJA (retirada)")
robot.MoveL(Pos_Approach_Caja)


# 11. POS_FOTO: regreso al punto de observación
print("→ POS_FOTO (fin del ciclo)")
robot.MoveJ(Pos_foto)

print("Secuencia finalizada correctamente.")

