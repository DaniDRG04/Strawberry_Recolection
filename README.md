# Strawberry Harvesting Robot — Autonomous Detection & Picking

An end-to-end system to detect ripeness and autonomously pick strawberries using a collaborative robot, computer vision, a soft-gripper end-effector with pneumatic actuation, and AI. The project also streams environmental data (temperature and humidity) to a database and dashboard for crop monitoring.

## Table of Contents
- [Overview](#overview)
- [Goals & Acceptance Criteria](#goals--acceptance-criteria)
- [In/Out of Scope](#inout-of-scope)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)

---

## Overview
This project builds an autonomous harvesting pipeline that:
1. Detects strawberry ripeness (unripe / ripe).
2. Plans and executes a safe pick with a soft pneumatic gripper on a cobot.
3. Records ambient/soil conditions (temperature, humidity) to inform cultivation via a dashboard.

The primary objective is a **gentle, damage-free harvest** with reliable classification and robust robot execution.

---

## Goals & Acceptance Criteria

### Goals
- End-to-end: perception → decision → manipulation → verification.   
- Gentle grasping and picking with a **soft pneumatic gripper**.  
- Continuous logging of **temperature & humidity** and publishing to a **database + dashboard**.

### Acceptance Criteria
1. A complete working system—cobot, vision, AI, soft-gripper pneumatics—able to classify by ripeness and pick **without damaging** the fruit.  
2. Environmental sensing (humidity & temperature) is **stored in a database** and **visible on a dashboard**.
   
---

## System Architecture
- **Perception & AI:** Vision pipeline (image acquisition, detection/classification, ripeness decision).  
- **Manipulation:** Soft-gripper with pneumatic actuation; pick path planning; tool & frame calibration.  
- **Robot Control:** UR-series cobot motion control, safety envelopes, approach/retreat, verification.  
- **IoT & Data:** Sensor ingestion (temperature, humidity) → database → dashboard visualizations.  

---

## Tech Stack
- **Robot:** UR3e
- **Perception:** OpenCV • YoloV8 • PnP    
- **End-Effector:** Soft pneumatic gripper (pump, valves, pressure sensors)  
- **Data:** Python ingest services • SQL DB • Dashboard (e.g., Grafana / Plotly / Dash)  
- **CAD:** SolidWorks & Fusion360 (design + manufacturing plan)
