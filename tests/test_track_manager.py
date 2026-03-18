"""
Tests for TrackManager.
"""

import pytest
import tempfile
import json
from pathlib import Path
from late_brake.track_manager import TrackManager
from late_brake.track import Track, Anchor


def test_track_manager_init():
    """Test that TrackManager can be initialized."""
    tm = TrackManager()
    assert tm is not None
    assert tm._built_in_dir is not None
    assert tm._user_dir.exists()  # User dir should be created if it doesn't exist


def test_list_tracks_returns_list():
    """Test that list_tracks returns a list."""
    tm = TrackManager()
    tracks = tm.list_tracks()
    assert isinstance(tracks, list)
    # May be empty if no built-in tracks yet, that's OK


def test_get_track_returns_none_for_nonexistent():
    """Test that get_track returns None for non-existent track."""
    tm = TrackManager()
    track = tm.get_track("nonexistent")
    assert track is None


def test_add_track_and_get_back():
    """Test adding a track and then getting it back."""
    tm = TrackManager()
    
    # Create a test track
    track = Track(
        id="test-track-123",
        name="Test Track",
        length_m=1000,
        turn_count=5,
        anchor=Anchor(lat=0, lon=0, radius_m=1000),
        gate=[[0, 0], [0.001, 0.001]],
        centerline=[[0, 0], [0.001, 0.001]]
    )
    
    # Add the track
    tm.add_track(track)
    
    # Get it back
    retrieved = tm.get_track("test-track-123")
    assert retrieved is not None
    assert retrieved.id == "test-track-123"
    assert retrieved.name == "Test Track"
    assert retrieved.length_m == 1000
    
    # Clean up: remove the test file
    test_file = tm._user_dir / "test-track-123.json"
    if test_file.exists():
        test_file.unlink()
