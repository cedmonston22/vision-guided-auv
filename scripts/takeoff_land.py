"""
Run PX4 SITL first, in a separate terminal:
 
    cd ~/PX4-Autopilot
    HEADLESS=1 make px4_sitl gz_x500_mono_cam_down

"""


from mavsdk import System
import asyncio

async def run():
    drone = System()
    await drone.connect()
    print("Drone Ready For Action")
    await drone.action.arm()
    
    await drone.action.set_takeoff_altitude(5)
    await drone.action.takeoff()
    
    await asyncio.sleep(10)
    async for pos in drone.telemetry.position():
        print(pos)
        break
        
    
    print("Landing")
    await drone.action.land()


if __name__ == "__main__":
    asyncio.run(run())
