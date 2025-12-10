"""
Detection modules for Safety Monitoring System
"""

from .people_detector import PeopleDetector
from .pose_detector import PoseDetector
from .ppe_detector import PPEDetector

__all__ = ['PeopleDetector', 'PoseDetector', 'PPEDetector']