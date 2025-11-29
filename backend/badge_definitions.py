"""
Badge definitions and requirements
"""

BADGES = {
    # Activity Count Badges
    "first_steps": {
        "id": "first_steps",
        "name": "First Steps",
        "description": "Log your first activity",
        "icon": "🎯",
        "category": "activity",
        "requirement_type": "activity_count",
        "requirement_value": 1,
        "rarity": "common"
    },
    "getting_started": {
        "id": "getting_started",
        "name": "Getting Started",
        "description": "Log 10 activities",
        "icon": "🌟",
        "category": "activity",
        "requirement_type": "activity_count",
        "requirement_value": 10,
        "rarity": "common"
    },
    "dedicated": {
        "id": "dedicated",
        "name": "Dedicated",
        "description": "Log 50 activities",
        "icon": "💪",
        "category": "activity",
        "requirement_type": "activity_count",
        "requirement_value": 50,
        "rarity": "rare"
    },
    "super_achiever": {
        "id": "super_achiever",
        "name": "Super Achiever",
        "description": "Log 100 activities",
        "icon": "🏆",
        "category": "activity",
        "requirement_type": "activity_count",
        "requirement_value": 100,
        "rarity": "epic"
    },
    "legendary_worker": {
        "id": "legendary_worker",
        "name": "Legendary Worker",
        "description": "Log 500 activities",
        "icon": "👑",
        "category": "activity",
        "requirement_type": "activity_count",
        "requirement_value": 500,
        "rarity": "legendary"
    },
    
    # Earnings Badges
    "first_dollar": {
        "id": "first_dollar",
        "name": "First Dollar",
        "description": "Earn your first dollar",
        "icon": "💵",
        "category": "earnings",
        "requirement_type": "total_earnings",
        "requirement_value": 1,
        "rarity": "common"
    },
    "money_maker": {
        "id": "money_maker",
        "name": "Money Maker",
        "description": "Earn $50",
        "icon": "💰",
        "category": "earnings",
        "requirement_type": "total_earnings",
        "requirement_value": 50,
        "rarity": "rare"
    },
    "big_earner": {
        "id": "big_earner",
        "name": "Big Earner",
        "description": "Earn $100",
        "icon": "💸",
        "category": "earnings",
        "requirement_type": "total_earnings",
        "requirement_value": 100,
        "rarity": "epic"
    },
    "wealth_builder": {
        "id": "wealth_builder",
        "name": "Wealth Builder",
        "description": "Earn $500",
        "icon": "🏦",
        "category": "earnings",
        "requirement_type": "total_earnings",
        "requirement_value": 500,
        "rarity": "legendary"
    },
    
    # Streak Badges
    "on_fire": {
        "id": "on_fire",
        "name": "On Fire",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "category": "streak",
        "requirement_type": "current_streak",
        "requirement_value": 7,
        "rarity": "rare"
    },
    "unstoppable": {
        "id": "unstoppable",
        "name": "Unstoppable",
        "description": "Maintain a 30-day streak",
        "icon": "⚡",
        "category": "streak",
        "requirement_type": "current_streak",
        "requirement_value": 30,
        "rarity": "epic"
    },
    "streak_master": {
        "id": "streak_master",
        "name": "Streak Master",
        "description": "Maintain a 100-day streak",
        "icon": "🌠",
        "category": "streak",
        "requirement_type": "current_streak",
        "requirement_value": 100,
        "rarity": "legendary"
    },
    
    # Reading Badges
    "bookworm": {
        "id": "bookworm",
        "name": "Bookworm",
        "description": "Read 100 pages",
        "icon": "📚",
        "category": "reading",
        "requirement_type": "pages_read",
        "requirement_value": 100,
        "rarity": "common"
    },
    "avid_reader": {
        "id": "avid_reader",
        "name": "Avid Reader",
        "description": "Read 500 pages",
        "icon": "📖",
        "category": "reading",
        "requirement_type": "pages_read",
        "requirement_value": 500,
        "rarity": "rare"
    },
    "library_master": {
        "id": "library_master",
        "name": "Library Master",
        "description": "Read 1000 pages",
        "icon": "🏛️",
        "category": "reading",
        "requirement_type": "pages_read",
        "requirement_value": 1000,
        "rarity": "epic"
    },
    
    # Special Badges
    "early_bird": {
        "id": "early_bird",
        "name": "Early Bird",
        "description": "Log an activity before 8 AM",
        "icon": "🌅",
        "category": "special",
        "requirement_type": "special",
        "requirement_value": 1,
        "rarity": "rare"
    },
    "night_owl": {
        "id": "night_owl",
        "name": "Night Owl",
        "description": "Log an activity after 10 PM",
        "icon": "🦉",
        "category": "special",
        "requirement_type": "special",
        "requirement_value": 1,
        "rarity": "rare"
    },
    "weekend_warrior": {
        "id": "weekend_warrior",
        "name": "Weekend Warrior",
        "description": "Log activities on both Saturday and Sunday",
        "icon": "🎮",
        "category": "special",
        "requirement_type": "special",
        "requirement_value": 1,
        "rarity": "rare"
    },
    "perfect_week": {
        "id": "perfect_week",
        "name": "Perfect Week",
        "description": "Log activities every day for a week",
        "icon": "✨",
        "category": "special",
        "requirement_type": "special",
        "requirement_value": 1,
        "rarity": "epic"
    },
    "goal_crusher": {
        "id": "goal_crusher",
        "name": "Goal Crusher",
        "description": "Complete your first savings goal",
        "icon": "🎊",
        "category": "special",
        "requirement_type": "goals_completed",
        "requirement_value": 1,
        "rarity": "rare"
    },
}

def get_all_badges():
    """Return all badge definitions"""
    return BADGES

def get_badge_by_id(badge_id: str):
    """Get a specific badge by ID"""
    return BADGES.get(badge_id)

def get_badges_by_category(category: str):
    """Get all badges in a category"""
    return {k: v for k, v in BADGES.items() if v["category"] == category}
