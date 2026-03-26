import os 
import yaml 
import threading
from typing import Optional, Any

ROOT_PATH = os.path.dirname(__file__)

class ApplicationConfig: 
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ApplicationConfig, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self): 
        if self._initialized:
            return
        
        self.file_config = self._load_config()
        
        self.FE_URL = self._load_variable("FE_URL", "http://localhost:3000")
        self.IS_HTTPS = self._to_bool(self._load_variable("IS_HTTPS", False))
        self.SAME_SITE = self._load_variable("SAME_SITE", "lax")

        # jwt
        self.ACCESS_TOKEN_KEY = self._load_variable("ACCESS_TOKEN_KEY", None)
        self.REFRESH_TOKEN_KEY = self._load_variable("REFRESH_TOKEN_KEY", None)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self._load_variable("ACCESS_TOKEN_EXPIRE_MINUTES", 20)
        self.REFRESH_TOKEN_EXPIRE_DAYS = self._load_variable("REFRESH_TOKEN_EXPIRE_DAYS", 15)
        self.ALGORITHM_HASH = self._load_variable("ALGORITHM_HASH", "HS256")

        # user
        self.MAX_FAILED_LOGIN_ATTEMPTS = self._load_variable("MAX_FAILED_LOGIN_ATTEMPTS", 5)
        self.LOCK_DURATION_MINUTES = self._load_variable("LOCK_DURATION_MINUTES", 30)

        # email
        self.EMAIL_USER = self._load_variable("EMAIL_USER", None)
        self.EMAIL_PASSWORD = self._load_variable("EMAIL_PASSWORD", None)

        # log level 
        self.LOG_LEVEL = self._load_variable("LOG_LEVEL", "INFO")
        
        # environment
        self.ENVIRONMENT = self._load_variable("ENVIRONMENT", "DEVELOPMENT")
 
        # database 
        self.DATABASE_URL = self._load_variable("DATABASE_URL", None)
        self.MIGRATION_DATABASE_URL = self._load_variable("MIGRATION_DATABASE_URL", None)
        
        self._initialized = True

    def _load_config(self) -> dict: 
        """ Load config from yaml file """
        config_path = os.path.join(ROOT_PATH, "env.yaml")
        if os.path.exists(config_path): 
            with open(config_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content if isinstance(content, dict) else {}
        return {}
    
    def _load_variable(self, key: str, default: Optional[Any]) -> Any:
        """ Load variable from environment or config file """
        var = os.getenv(key)

        if var is None:
            var = self.file_config.get(key, default)

        if var is None:
            self._raise_error(key)
            
        return var
    
    def _to_bool(self, val: Any) -> bool:
        """ Convert value boolean of yaml file or environment variable to boolean """
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "yes", "on")

    def _raise_error(self, key: str):
        """ Raise error if variable is missing """
        raise ValueError(f"Missing required configuration: {key}")
    

# initialize singleton instance 
app_config = ApplicationConfig()