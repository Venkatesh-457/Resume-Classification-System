"""
Profile Repository Module
Handles profile creation, active profile selection, listing, and deletion.
"""

import logging
from data_access.database import get_connection

logger = logging.getLogger(__name__)


class ProfileRepository:
    """Data access layer for managing local user profiles."""

    @staticmethod
    def list_profiles() -> list[dict]:
        """Fetch all registered profiles sorted by name."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, is_active, created_at FROM profiles ORDER BY name ASC;")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_active_profile() -> dict:
        """Fetch the currently active profile, or activate the first profile if none active."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, is_active, created_at FROM profiles WHERE is_active = 1 LIMIT 1;")
            row = cursor.fetchone()
            if row:
                return dict(row)

            # Fallback to first available profile
            cursor.execute("SELECT id, name, is_active, created_at FROM profiles ORDER BY id ASC LIMIT 1;")
            first_row = cursor.fetchone()
            if first_row:
                profile_id = first_row["id"]
                cursor.execute("UPDATE profiles SET is_active = 1 WHERE id = ?;", (profile_id,))
                conn.commit()
                return dict(first_row)

            # If empty, create default
            cursor.execute("INSERT INTO profiles (name, is_active) VALUES (?, 1);", ("Default Profile",))
            conn.commit()
            cursor.execute("SELECT id, name, is_active, created_at FROM profiles WHERE is_active = 1 LIMIT 1;")
            return dict(cursor.fetchone())

    @staticmethod
    def set_active_profile(profile_id: int) -> bool:
        """Set a given profile as active and deactivate all others."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM profiles WHERE id = ?;", (profile_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("UPDATE profiles SET is_active = 0;")
            cursor.execute("UPDATE profiles SET is_active = 1 WHERE id = ?;", (profile_id,))
            conn.commit()
            return True

    @staticmethod
    def create_profile(name: str) -> int:
        """Create a new profile. Returns new profile id."""
        name = name.strip()
        if not name:
            raise ValueError("Profile name cannot be blank.")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO profiles (name, is_active) VALUES (?, 0);", (name,))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def delete_profile(profile_id: int) -> bool:
        """
        Delete a profile and its associated analyses via CASCADE.
        Prevents deleting the last remaining profile.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM profiles;")
            count = cursor.fetchone()[0]
            if count <= 1:
                raise ValueError("Cannot delete the only remaining profile.")

            cursor.execute("SELECT is_active FROM profiles WHERE id = ?;", (profile_id,))
            target = cursor.fetchone()
            if not target:
                return False

            was_active = bool(target["is_active"])
            cursor.execute("DELETE FROM profiles WHERE id = ?;", (profile_id,))

            if was_active:
                # Activate another profile
                cursor.execute("UPDATE profiles SET is_active = 1 WHERE id = (SELECT id FROM profiles LIMIT 1);")

            conn.commit()
            return True
