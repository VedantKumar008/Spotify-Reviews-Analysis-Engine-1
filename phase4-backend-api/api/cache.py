"""
Caching Module for Backend API
Phase 4: Backend API Development
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


class ResultCache:
    """In-memory and file-based cache for workflow results."""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_seconds: int = 3600):
        """
        Initialize the result cache.
        
        Args:
            cache_dir: Directory for persistent cache storage
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, workflow_params: Dict) -> str:
        """
        Generate a cache key from workflow parameters.
        
        Args:
            workflow_params: Dictionary of workflow parameters
            
        Returns:
            Cache key string
        """
        # Sort parameters to ensure consistent key generation
        params_str = json.dumps(workflow_params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def get(self, workflow_params: Dict) -> Optional[Dict]:
        """
        Get cached result if available and not expired.
        
        Args:
            workflow_params: Workflow parameters
            
        Returns:
            Cached result or None if not found/expired
        """
        key = self._generate_key(workflow_params)
        
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if self._is_valid(entry):
                return entry["data"]
            else:
                # Remove expired entry
                del self.memory_cache[key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                if self._is_valid(entry):
                    # Load into memory cache
                    self.memory_cache[key] = entry
                    return entry["data"]
                else:
                    # Remove expired file
                    cache_file.unlink()
            except Exception:
                # If file is corrupted, remove it
                cache_file.unlink()
        
        return None
    
    def set(self, workflow_params: Dict, data: Dict):
        """
        Cache a result.
        
        Args:
            workflow_params: Workflow parameters
            data: Result data to cache
        """
        key = self._generate_key(workflow_params)
        entry = {
            "data": data,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=self.ttl_seconds)).isoformat()
        }
        
        # Store in memory
        self.memory_cache[key] = entry
        
        # Store in file
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2)
    
    def _is_valid(self, entry: Dict) -> bool:
        """
        Check if a cache entry is still valid.
        
        Args:
            entry: Cache entry
            
        Returns:
            True if entry is valid, False otherwise
        """
        expires_at = entry.get("expires_at")
        if not expires_at:
            return False
        
        try:
            expiry_time = datetime.fromisoformat(expires_at)
            return datetime.now() < expiry_time
        except Exception:
            return False
    
    def clear(self):
        """Clear all cache entries."""
        self.memory_cache.clear()
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def clear_expired(self):
        """Clear only expired cache entries."""
        # Clear expired memory entries
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if not self._is_valid(entry)
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Clear expired file entries
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                if not self._is_valid(entry):
                    cache_file.unlink()
            except Exception:
                cache_file.unlink()
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        file_count = len(list(self.cache_dir.glob("*.json")))
        
        return {
            "memory_cache_size": len(self.memory_cache),
            "file_cache_size": file_count,
            "ttl_seconds": self.ttl_seconds
        }


# Global cache instance
result_cache = ResultCache()
