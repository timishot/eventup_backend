from django.db.models import Q
from .models import User

def jaccard_similarity(list1, list2):
    set1, set2 = set(list1), set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0

def get_networking_suggestions(user, top_n=5):
    """
    Suggest users based on shared interests and profession.
    Args:
        user: The current user (User object)
        top_n: Number of suggestions to return
    Returns:
        List of (User, similarity_score) tuples
    """
    # Get all active users except the current user
    users = User.objects.filter(is_active=True).exclude(id=user.id)
    if not users.exists():
        return []

    suggestions = []
    user_interests = set(user.interests)
    user_profession = user.profession.lower() if user.profession else ''

    for other_user in users:
        other_interests = set(other_user.interests)
        other_profession = other_user.profession.lower() if other_user.profession else ''

        # Calculate similarity for interests
        interest_similarity = jaccard_similarity(user_interests, other_interests)

        # Calculate similarity for profession (1 if same, 0 if different)
        profession_similarity = 1 if user_profession == other_profession and user_profession else 0

        # Weighted average (70% interests, 30% profession)
        similarity = 0.7 * interest_similarity + 0.3 * profession_similarity

        if similarity > 0:
            suggestions.append((other_user, similarity))

    # Sort by similarity and limit to top_n
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions[:top_n]