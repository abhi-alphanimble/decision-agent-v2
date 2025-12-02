# Config logging functions to add to crud.py

# Add this after the update_channel_config function (around line 570)

def log_config_change(
    db: Session,
    channel_id: str,
    setting_name: str,
    old_value: int,
    new_value: int,
    changed_by: str,
    changed_by_name: str
) -> Optional[ConfigChangeLog]:
    """
    Log a configuration change to the audit trail.
    
    Args:
        db: Database session
        channel_id: Channel ID where config was changed
        setting_name: Name of the setting (approval_percentage, auto_close_hours, group_size)
        old_value: Previous value
        new_value: New value
        changed_by: User ID who made the change
        changed_by_name: Username for display
    
    Returns:
        ConfigChangeLog object or None on error
    """
    try:
        log_entry = ConfigChangeLog(
            channel_id=channel_id,
            setting_name=setting_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            changed_by_name=changed_by_name,
            changed_at=datetime.utcnow()
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        logger.info(
            f"📝 Logged config change: {channel_id} - {setting_name}: "
            f"{old_value} → {new_value} by {changed_by_name}"
        )
        
        return log_entry
    except Exception as e:
        logger.error(f"Error logging config change: {str(e)}")
        db.rollback()
        return None


def get_config_change_logs(
    db: Session,
    channel_id: str,
    limit: int = 50
) -> List[ConfigChangeLog]:
    """
    Get config change history for a channel.
    
    Args:
        db: Database session
        channel_id: Channel ID
        limit: Maximum number of logs to return (default 50)
    
    Returns:
        List of ConfigChangeLog objects, newest first
    """
    try:
        return (
            db.query(ConfigChangeLog)
            .filter(ConfigChangeLog.channel_id == channel_id)
            .order_by(ConfigChangeLog.changed_at.desc())
            .limit(limit)
            .all()
        )
    except Exception as e:
        logger.error(f"Error fetching config change logs: {str(e)}\"")
        return []


# Replace the update_channel_config function with this version:

def update_channel_config(
    db: Session,
    channel_id: str,
    updated_by: str,
    updated_by_name: str = None,
    **kwargs
) -> Optional[ChannelConfig]:
    """
    Update channel configuration settings.
    Logs all changes to ConfigChangeLog table.
    """
    try:
        config = get_channel_config(db, channel_id)
        
        # Track changes for logging
        changes = []
        
        # Update fields if provided and track changes
        if 'approval_percentage' in kwargs:
            old_value = config.approval_percentage
            new_value = kwargs['approval_percentage']
            if old_value != new_value:
                config.approval_percentage = new_value
                changes.append(('approval_percentage', old_value, new_value))
        
        if 'auto_close_hours' in kwargs:
            old_value = config.auto_close_hours
            new_value = kwargs['auto_close_hours']
            if old_value != new_value:
                config.auto_close_hours = new_value
                changes.append(('auto_close_hours', old_value, new_value))
        
        if 'group_size' in kwargs:
            old_value = config.group_size
            new_value = kwargs['group_size']
            if old_value != new_value:
                config.group_size = new_value
                changes.append(('group_size', old_value, new_value))
        
        config.updated_by = updated_by
        config.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(config)
        
        # Log all changes
        for setting_name, old_val, new_val in changes:
            log_config_change(
                db=db,
                channel_id=channel_id,
                setting_name=setting_name,
                old_value=old_val,
                new_value=new_val,
                changed_by=updated_by,
                changed_by_name=updated_by_name or updated_by
            )
        
        logger.info(f"✅ Updated config for channel {channel_id} by {updated_by}")
        return config
    except Exception as e:
        logger.error(f"Database error in update_channel_config: {str(e)}")
        db.rollback()
        return None
