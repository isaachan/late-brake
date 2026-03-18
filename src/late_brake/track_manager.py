"""
Track manager - handles loading and managing track definitions.
Supports built-in tracks and user-defined custom tracks.
"""

import os
import json
from typing import List, Optional
from pathlib import Path

from late_brake.track import Track


class TrackManager:
    """
    Manages track definitions.
    Looks for tracks in:
    1. Built-in tracks: package data/tracks/
    2. User custom tracks: ~/.late-brake/tracks/
    """
    
    def __init__(self):
        self._built_in_dir = self._get_built_in_dir()
        self._user_dir = self._get_user_dir()
        self._cache: Optional[List[Track]] = None
    
    def _get_built_in_dir(self) -> Path:
        """Get the built-in tracks directory."""
        # Get package directory
        package_dir = Path(__file__).parent
        return package_dir / "data" / "tracks"
    
    def _get_user_dir(self) -> Path:
        """Get the user custom tracks directory."""
        home = Path.home()
        user_dir = home / ".late-brake" / "tracks"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _load_all_tracks(self) -> List[Track]:
        """Load all tracks from both built-in and user directories."""
        tracks = []
        
        # Load built-in tracks
        if self._built_in_dir.exists():
            for file in self._built_in_dir.glob("*.json"):
                try:
                    track = self._load_track_from_file(file)
                    if track:
                        tracks.append(track)
                except Exception:
                    # Skip invalid tracks
                    pass
        
        # Load user tracks (override built-in with same ID)
        if self._user_dir.exists():
            for file in self._user_dir.glob("*.json"):
                try:
                    track = self._load_track_from_file(file)
                    if track:
                        # Remove any existing track with same ID
                        tracks = [t for t in tracks if t.id != track.id]
                        tracks.append(track)
                except Exception:
                    # Skip invalid tracks
                    pass
        
        # Sort by ID
        tracks.sort(key=lambda t: t.id)
        return tracks
    
    def _load_track_from_file(self, file_path: Path) -> Optional[Track]:
        """Load a track from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Track.model_validate(data)
    
    def list_tracks(self) -> List[Track]:
        """List all available tracks."""
        if self._cache is None:
            self._cache = self._load_all_tracks()
        return self._cache
    
    def get_track(self, track_id: str) -> Optional[Track]:
        """Get a specific track by ID."""
        tracks = self.list_tracks()
        for track in tracks:
            if track.id == track_id:
                return track
        return None
    
    def add_track(self, track: Track) -> None:
        """Add or update a track in user directory."""
        file_path = self._user_dir / f"{track.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(track.model_dump(), f, indent=2, ensure_ascii=False)
        # Invalidate cache
        self._cache = None
