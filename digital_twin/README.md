# Digital Twin (RoboDK)

A **digital twin** was implemented in **RoboDK** to simulate the full harvesting cycle (perception → approach → pick → place) in a controlled environment **without using physical hardware**. This enables:
- Validating the **robot routine** and motion logic safely.
- Tuning **frames/tool** (T_base / T_tool) and approach/retreat sequences before field tests.
- Running fast iterations with **scenario variants** (lighting, occlusions, pose noise) without risking equipment.

---

## Folder Contents

- **RoboDK Station (.rdk):** Robot cell with TCP, objects, and cycle targets.
- **CAD Models:** Parts used by the twin (plants, fixtures, gripper, table).
- **Simulation Scripts:** Utilities to launch and verify the picking routine.
