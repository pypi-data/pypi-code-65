import asyncio
import platform

import psutil

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "Probe Health"

    @property
    def kind(self) -> str:
        return "mpprobehealth"

    @property
    def definition(self) -> dict:
        probe_health_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Internal sensor used to monitor the health of a PRTG probe on the system "
            "the mini probe is running on",
            default="yes",
            sensor_help="Internal sensor used to monitor the health of a PRTG probe on the system "
            "the mini probe is running on",
            tag="mpprobehealthsensor",
        )
        probe_health_def_group_temperature = SensorDefinitionGroup(name="temperature", caption="Temperature Settings")
        probe_health_def_group_temperature.add_field(
            field_type="radio",
            name="celfar",
            caption="Choose between Celsius or Fahrenheit display",
            help="Choose wether you want to return the value in Celsius or Fahrenheit",
            options={"1": "Celsius", "2": "Fahrenheit"},
            default="1",
        )
        probe_health_def_group_temperature.add_field(
            field_type="radio",
            name="diskfull",
            caption="Full Display of all disk space values",
            help="Choose wether you want to get all disk space data or only percentages.",
            options={"1": "Percentages", "2": "Full Information"},
            default="1",
        )
        probe_health_def.add_group(probe_health_def_group_temperature)
        return probe_health_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        probe_health_data = SensorData(sensor_id=task_data["sensorid"])
        uname = platform.uname()
        probe_health_data.message = f"Running on {uname.system} in version {uname.version}! OK"
        cpu_load = psutil.getloadavg()
        vmemory = psutil.virtual_memory()
        swapmemory = psutil.swap_memory()
        disk_partitions = psutil.disk_partitions()
        for partition in disk_partitions:
            part_disk_usage = psutil.disk_usage(partition[1])
            probe_health_data.add_channel(
                name=f"Disk Space Percent {partition[1]}",
                mode="float",
                kind="Percent",
                value=part_disk_usage[3],
            )
            if task_data["diskfull"] == "2":
                probe_health_data.add_channel(
                    name=f"Disk Space Total {partition[1]}",
                    mode="integer",
                    kind="BytesDisk",
                    value=part_disk_usage[0],
                )

                probe_health_data.add_channel(
                    name=f"Disk Space Used {partition[1]}",
                    mode="integer",
                    kind="BytesDisk",
                    value=part_disk_usage[1],
                )
                probe_health_data.add_channel(
                    name=f"Disk Space Free {partition[1]}",
                    mode="integer",
                    kind="BytesDisk",
                    value=part_disk_usage[2],
                )

        probe_health_data.add_channel(name="Memory Total", mode="integer", kind="BytesMemory", value=vmemory.total)
        probe_health_data.add_channel(
            name="Memory Available",
            mode="integer",
            kind="BytesMemory",
            value=vmemory.available,
        )
        probe_health_data.add_channel(
            name="Swap Total",
            mode="integer",
            kind="BytesMemory",
            value=swapmemory.total,
        )
        probe_health_data.add_channel(name="Swap Free", mode="integer", kind="BytesMemory", value=swapmemory.free)
        probe_health_data.add_channel(
            name="Load average 1 min",
            mode="float",
            kind="Custom",
            customunit="",
            value=float(cpu_load[0]),
        )
        probe_health_data.add_channel(
            name="Load average 5 min",
            mode="float",
            kind="Custom",
            customunit="",
            value=float(cpu_load[1]),
        )
        probe_health_data.add_channel(
            name="Load average 10 min",
            mode="float",
            kind="Custom",
            customunit="",
            value=float(cpu_load[2]),
        )
        await q.put(probe_health_data.data)
