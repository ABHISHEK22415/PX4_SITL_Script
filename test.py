#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan


async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))
    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))

    # Load waypoints dynamically from waypoints.txt
    mission_items = await load_waypoints_from_file("waypoints.txt")
    mission_plan = MissionPlan(mission_items)

    # Enable Return-to-Launch (RTL) after mission completion
    await drone.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()

    await termination_task


async def load_waypoints_from_file(file_path):
    """
    Reads waypoints from a file and returns a list of MissionItem objects.
    File format: latitude,longitude,altitude
    """
    mission_items = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                lat, lon, alt = map(float, line.strip().split(","))
                mission_items.append(
                    MissionItem(
                        lat, lon, alt,
                        speed_m_s=10,
                        is_fly_through=True,
                        gimbal_pitch_deg=float('nan'),
                        gimbal_yaw_deg=float('nan'),
                        camera_action=MissionItem.CameraAction.NONE,
                        loiter_time_s=float('nan'),
                        camera_photo_interval_s=float('nan'),
                        acceptance_radius_m=float('nan'),
                        yaw_deg=float('nan'),
                        camera_photo_distance_m=float('nan'),
                        vehicle_action=MissionItem.VehicleAction.NONE
                    )
                )
    except FileNotFoundError:
        print(f"Error: {file_path} not found!")
    except ValueError as e:
        print(f"Error reading waypoints: {e}")
    return mission_items


async def print_mission_progress(drone):
    """ Prints mission progress """
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")


async def observe_is_in_air(drone, running_tasks):
    """
    Monitors whether the drone is flying or not and
    returns after landing.
    """
    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = True

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()
            return


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
