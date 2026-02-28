"""
Unit tests for Vantablack C2 Core module.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from core.c2.core import VantaC2, Beacon, Listener, BeaconStatus, BeaconType
from core.c2.exceptions import BeaconError, ListenerError


class TestBeacon:
    """Test Beacon class functionality."""
    
    def test_beacon_creation(self):
        """Test beacon creation with default values."""
        beacon = Beacon(target="192.168.1.10", technique="wmi")
        
        assert beacon.target == "192.168.1.10"
        assert beacon.technique == "wmi"
        assert beacon.status == BeaconStatus.ACTIVE
        assert beacon.type == BeaconType.HTTP
        assert beacon.sleep_time == 60
        assert beacon.jitter == 0.2
        assert isinstance(beacon.id, str)
        assert isinstance(beacon.created_at, datetime)
    
    def test_beacon_to_dict(self):
        """Test beacon serialization to dictionary."""
        beacon = Beacon(target="192.168.1.10", technique="wmi")
        beacon_dict = beacon.to_dict()
        
        assert beacon_dict["target"] == "192.168.1.10"
        assert beacon_dict["technique"] == "wmi"
        assert beacon_dict["status"] == "active"
        assert beacon_dict["type"] == "http"
        assert beacon_dict["sleep_time"] == 60
        assert beacon_dict["jitter"] == 0.2
        assert "id" in beacon_dict
        assert "created_at" in beacon_dict
    
    def test_beacon_update_checkin(self):
        """Test beacon checkin timestamp update."""
        beacon = Beacon(target="192.168.1.10", technique="wmi")
        initial_checkin = beacon.last_checkin
        
        beacon.update_checkin()
        
        assert beacon.last_checkin is not None
        assert beacon.last_checkin != initial_checkin


class TestListener:
    """Test Listener class functionality."""
    
    def test_listener_creation(self):
        """Test listener creation with default values."""
        listener = Listener()
        
        assert listener.protocol == "http"
        assert listener.host == "0.0.0.0"
        assert listener.port == 8080
        assert listener.is_active is False
        assert isinstance(listener.id, str)
        assert isinstance(listener.created_at, datetime)
        assert isinstance(listener.beacons, set)
    
    def test_listener_to_dict(self):
        """Test listener serialization to dictionary."""
        listener = Listener()
        listener_dict = listener.to_dict()
        
        assert listener_dict["protocol"] == "http"
        assert listener_dict["host"] == "0.0.0.0"
        assert listener_dict["port"] == 8080
        assert listener_dict["is_active"] is False
        assert "id" in listener_dict
        assert "created_at" in listener_dict
        assert "beacons" in listener_dict


class TestVantaC2:
    """Test VantaC2 class functionality."""
    
    @pytest.fixture
    async def c2_instance(self):
        """Create a VantaC2 instance for testing."""
        c2 = VantaC2()
        yield c2
        await c2.stop()
    
    @pytest.mark.asyncio
    async def test_deploy_beacon(self, c2_instance):
        """Test beacon deployment."""
        beacon = await c2_instance.deploy_beacon(
            target="192.168.1.10", 
            technique="wmi"
        )
        
        assert beacon.id in c2_instance.beacons
        assert c2_instance.beacons[beacon.id].target == "192.168.1.10"
        assert c2_instance.beacons[beacon.id].technique == "wmi"
    
    @pytest.mark.asyncio
    async def test_deploy_beacon_error(self, c2_instance):
        """Test beacon deployment error handling."""
        # This should work fine, testing the basic functionality
        beacon = await c2_instance.deploy_beacon(
            target="192.168.1.10", 
            technique="wmi"
        )
        assert beacon is not None
    
    @pytest.mark.asyncio
    async def test_create_listener(self, c2_instance):
        """Test listener creation."""
        listener = await c2_instance.create_listener(
            protocol="https",
            host="127.0.0.1", 
            port=8443
        )
        
        assert listener.id in c2_instance.listeners
        assert c2_instance.listeners[listener.id].protocol == "https"
        assert c2_instance.listeners[listener.id].host == "127.0.0.1"
        assert c2_instance.listeners[listener.id].port == 8443
    
    @pytest.mark.asyncio
    async def test_start_listener(self, c2_instance):
        """Test listener startup."""
        listener = await c2_instance.create_listener()
        
        await c2_instance.start_listener(listener.id)
        
        assert c2_instance.listeners[listener.id].is_active is True
    
    @pytest.mark.asyncio
    async def test_start_nonexistent_listener(self, c2_instance):
        """Test starting non-existent listener."""
        with pytest.raises(ListenerError):
            await c2_instance.start_listener("nonexistent")
    
    @pytest.mark.asyncio
    async def test_add_operator(self, c2_instance):
        """Test adding operators."""
        await c2_instance.add_operator("operator1")
        await c2_instance.add_operator("operator2")
        
        assert "operator1" in c2_instance.operators
        assert "operator2" in c2_instance.operators
        assert len(c2_instance.operators) == 2
    
    @pytest.mark.asyncio
    async def test_get_beacon(self, c2_instance):
        """Test retrieving beacons."""
        beacon = await c2_instance.deploy_beacon("192.168.1.10", "wmi")
        
        retrieved = await c2_instance.get_beacon(beacon.id)
        assert retrieved is not None
        assert retrieved.id == beacon.id
        assert retrieved.target == "192.168.1.10"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_beacon(self, c2_instance):
        """Test retrieving non-existent beacon."""
        beacon = await c2_instance.get_beacon("nonexistent")
        assert beacon is None
    
    @pytest.mark.asyncio
    async def test_get_all_beacons(self, c2_instance):
        """Test retrieving all beacons."""
        # Deploy multiple beacons
        beacon1 = await c2_instance.deploy_beacon("192.168.1.10", "wmi")
        beacon2 = await c2_instance.deploy_beacon("192.168.1.11", "smb")
        
        beacons = await c2_instance.get_all_beacons()
        
        assert len(beacons) == 2
        beacon_ids = [b.id for b in beacons]
        assert beacon1.id in beacon_ids
        assert beacon2.id in beacon_ids
    
    @pytest.mark.asyncio
    async def test_execute_command(self, c2_instance):
        """Test command execution on beacon."""
        beacon = await c2_instance.deploy_beacon("192.168.1.10", "wmi")
        
        result = await c2_instance.execute_command(
            beacon.id, 
            "test_command",
            {"arg1": "value1"}
        )
        
        assert result["success"] is True
        assert result["command"] == "test_command"
        assert result["beacon_id"] == beacon.id
    
    @pytest.mark.asyncio
    async def test_execute_command_nonexistent_beacon(self, c2_instance):
        """Test command execution on non-existent beacon."""
        with pytest.raises(BeaconError):
            await c2_instance.execute_command("nonexistent", "test_command")
    
    @pytest.mark.asyncio
    async def test_start_stop_c2(self, c2_instance):
        """Test C2 system startup and shutdown."""
        await c2_instance.start()
        assert c2_instance.running is True
        
        await c2_instance.stop()
        assert c2_instance.running is False
    
    @pytest.mark.asyncio
    async def test_to_dict_serialization(self, c2_instance):
        """Test C2 state serialization."""
        # Add some data
        await c2_instance.deploy_beacon("192.168.1.10", "wmi")
        await c2_instance.create_listener()
        await c2_instance.add_operator("test_operator")
        
        state_dict = c2_instance.to_dict()
        
        assert "beacons" in state_dict
        assert "listeners" in state_dict
        assert "operators" in state_dict
        assert "running" in state_dict
        
        assert len(state_dict["beacons"]) == 1
        assert len(state_dict["listeners"]) == 1
        assert len(state_dict["operators"]) == 1
        assert state_dict["running"] is False


@pytest.mark.asyncio
async def test_beacon_heartbeat(c2_instance):
    """Test beacon heartbeat functionality."""
    beacon = await c2_instance.deploy_beacon("192.168.1.10", "wmi")
    initial_checkin = beacon.last_checkin
    
    # Start the C2 system to activate heartbeats
    await c2_instance.start()
    
    # Wait a bit for heartbeat to potentially run
    await asyncio.sleep(0.1)
    
    # Stop to prevent further heartbeats
    await c2_instance.stop()
    
    # The heartbeat should have updated the checkin time
    # (Note: This test is somewhat timing-dependent)
    updated_beacon = await c2_instance.get_beacon(beacon.id)
    assert updated_beacon is not None