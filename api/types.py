from enum import Enum

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    RED_TEAM = "red_team"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(str, Enum):
    """System permissions"""
    # Template permissions
    TEMPLATE_CREATE = "template_create"
    TEMPLATE_READ = "template_read"
    TEMPLATE_UPDATE = "template_update"
    TEMPLATE_DELETE = "template_delete"
    
    # Campaign permissions
    CAMPAIGN_CREATE = "campaign_create"
    CAMPAIGN_READ = "campaign_read"
    CAMPAIGN_UPDATE = "campaign_update"
    CAMPAIGN_DELETE = "campaign_delete"
    CAMPAIGN_EXECUTE = "campaign_execute"
    
    # Analysis permissions
    ANALYSIS_RUN = "analysis_run"
    ANALYSIS_READ = "analysis_read"
    
    # Marketplace permissions
    MARKETPLACE_READ = "marketplace_read"
    MARKETPLACE_SUBMIT = "marketplace_submit"
    MARKETPLACE_MODERATE = "marketplace_moderate"
    
    # System permissions
    SYSTEM_ADMIN = "system_admin"
    USER_MANAGE = "user_manage"
    SYSTEM_MONITOR = "system_monitor"
