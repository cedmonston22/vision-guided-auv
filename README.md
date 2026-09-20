# Vision-Guided UAV Autonomy (PX4 SITL)

A vision-guided autonomy stack for a simulated multirotor, built on PX4 and Gazebo.
The aircraft uses a downward-facing camera to detect, track, and land on a target, and
ultimately to navigate with GPS disabled using vision-based state estimation.

All work is developed and validated in PX4 Software-In-The-Loop (SITL) with Gazebo.
No hardware flight testing has been performed.

## Running it

See [COMMANDS.md](COMMANDS.md) for setup and the startup sequence.

## Why this exists

PX4 is the production flight stack that runs on real Pixhawk hardware. The offboard
control interface, the MAVLink protocol, the EKF2 estimator, and its external vision
inputs are the same code paths used in the field. Developing against them in simulation
is how autonomy work is actually done, because flight time is scarce and crashes are
expensive.

## Architecture

```
  Gazebo (camera sensor)
        |
        v
  Perception  ......  ArUco detection, pixel error
        |
        v
  Controller  ......  error -> velocity setpoint (offboard)
        |
        v
  PX4 SITL    ......  EKF2 state estimation, attitude control
        |
        v
  Logger      ......  structured flight records -> replay / analysis
```

Perception and control run on the "companion computer" side in Python. PX4 handles
hard real-time stabilization and state estimation. The two communicate over MAVLink.

## Milestones

Each milestone is complete only when it works on unrehearsed runs and has measured
numbers attached. "It worked once" does not count.

### M0: Environment
PX4 SITL and Gazebo running with hardware-accelerated rendering. A MAVSDK script that
connects, arms, takes off, hovers, and lands.

**Done when:** renderer reports real GPU acceleration (not llvmpipe), sim runs near
real time, takeoff-and-land script succeeds three consecutive times.

### M1: Perception
Camera frames from Gazebo into Python. ArUco detection. Pixel error computed and
characterized.

**Done when:** detection rate table across altitudes (3m/5m/10m/15m) and marker sizes,
measured per-frame detection latency, recorded overlay video.

### M2: Closed-loop position hold
Offboard velocity control driven entirely by image error. Aircraft acquires the marker
and holds above it.

**Done when:** converges and holds 60s with bounded error across 10+ runs from varied
starting offsets. Steady-state hold error, control loop rate, and perception-to-actuation
latency all measured. Error-vs-time plot shows convergence without sustained oscillation.

*This is the first milestone worth putting on a resume.*

### M3: Robustness and flight data pipeline
Detection-loss handling: hold, then climb to widen field of view, then reacquire.
Structured logging of every run. Replay tool producing error plots and ground tracks.

**Done when:** recovery time after occlusion is measured, and a logged run can be
replayed into plots without the simulator.

### M4: Moving target and precision landing
Track a marker moving at walking pace. Separately, descend and land on a static marker.

**Done when:** sustained tracking of a moving target, and touchdown within a stated
distance of marker center across 10 attempts.

Note: a pure proportional controller will trail a constant-velocity target by a fixed
offset forever. Solving that (integral term, or target velocity feedforward) is the
lesson of this milestone.

### M5: Optical flow position hold
First GPS-denied flight. Downward optical flow for velocity plus rangefinder for scale,
GPS fusion disabled.

**Done when:** holds position 60s with GPS off, drift measured in meters.

### M6: VIO waypoint navigation
Off-the-shelf VIO publishing pose, PX4 fusing it, multi-waypoint route flown GPS-denied.

**Done when:** route completed and returned near start, position drift stated as a
percentage of distance traveled, degradation conditions documented.

## Known limitations

Simulation does not reproduce the conditions that make vision-based estimation hard on
real aircraft:

- **Vibration.** Simulated IMU data is clean. Real IMUs sit on an airframe with four
  motors spinning, and vibration is a primary cause of VIO failure in practice.
- **Rolling shutter.** Simulated cameras have global shutter. Real rolling-shutter
  sensors smear geometry during fast motion.
- **Lighting and motion blur.** Simulated exposure is ideal.
- **Texture.** Real environments include blank concrete and featureless grass where
  there is nothing to track.

Deliberately degrading test conditions in Gazebo (wind, lighting, low-texture worlds)
and documenting where the estimate breaks is more valuable than a clean happy-path result.

## Results

| Milestone | Metric | Value |
|---|---|---|
| M1 | Detection rate @ 5m | |
| M1 | Detection latency | |
| M2 | Steady-state hold error | |
| M2 | Control loop rate | |
| M2 | Perception-to-actuation latency | |
| M3 | Recovery time after occlusion | |
| M4 | Landing accuracy | |
| M5 | Drift over 60s, GPS denied | |
| M6 | Position drift, % of distance | |

## Log

Running record of what was tried, what the numbers were, and what broke. Kept current
per milestone rather than reconstructed at the end.