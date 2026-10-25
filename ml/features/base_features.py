"""
Base class for all feature generators.
Provides common functionality and interface for feature calculation.
"""
import pandas as pd
import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseFeatures(ABC):
    """Abstract base class for feature generators"""
    
    windows = [5]

    def __init__(self):
        self.feature_names = self._get_feature_names()
    
    @abstractmethod
    def _get_feature_names(self) -> list:
        """Return list of feature names this class generates"""
        pass
    
    @abstractmethod
    def calculate_features(self, **kwargs) -> Dict[str, Any]:
        """Calculate all features for this category"""
        pass

    def _handle_no_data(self, default_value=0) -> Dict[str, Any]:
        """Return dictionary with default values when no historical data exists"""
        return {name: default_value for name in self.feature_names}