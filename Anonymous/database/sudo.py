# (©) Anonymous Emperor 

from Anonymous.database.imposter import mongo
from typing import Dict, List, Union

sudoersdb = mongo.sudoersdb


async def get_sudoers() -> list:
    """
    Fetches the list of sudo users from the database.
    """
    sudoers_data = await sudoersdb.find_one({"sudo": "sudo"})
    if sudoers_data and "sudoers" in sudoers_data:
        return sudoers_data["sudoers"]
    return []


async def add_sudo(user_id: int) -> bool:
    """
    Adds a user to the sudoers list in the database.

    Args:
        user_id (int): The user ID to be added to the sudoers list.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    sudoers = await get_sudoers()
    if user_id in sudoers:
        return False  # Already a sudo user
    sudoers.append(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def remove_sudo(user_id: int) -> bool:
    """
    Removes a user from the sudoers list in the database.

    Args:
        user_id (int): The user ID to be removed from the sudoers list.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    sudoers = await get_sudoers()
    if user_id not in sudoers:
        return False  # Not a sudo user
    sudoers.remove(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True
