from django.test import TestCase
from datetime import date, timedelta
from .scoring import ScoringService

class ScoringServiceTest(TestCase):
    def setUp(self):
        self.today = date.today()

    def test_urgency_scoring(self):
        """Test that urgent tasks score higher than non-urgent ones"""
        task_urgent = {
            "id": 1,
            "title": "Urgent",
            "due_date": self.today, # Due today
            "importance": 5,
            "estimated_hours": 1,
            "dependencies": []
        }
        task_later = {
            "id": 2,
            "title": "Later",
            "due_date": self.today + timedelta(days=10),
            "importance": 5,
            "estimated_hours": 1,
            "dependencies": []
        }
        
        results = ScoringService.analyze_tasks([task_urgent, task_later])
        
        # Urgent task should have a higher score
        self.assertTrue(results[0]['priority_score'] > results[1]['priority_score'])
        self.assertEqual(results[0]['id'], 1)

    def test_dependency_weight(self):
        """Test that tasks blocking others get a score boost"""
        # Task A blocks Task B
        task_blocker = {
            "id": 1, "title": "Blocker", "due_date": self.today + timedelta(days=5),
            "importance": 5, "estimated_hours": 1, "dependencies": []
        }
        task_blocked = {
            "id": 2, "title": "Blocked", "due_date": self.today + timedelta(days=5),
            "importance": 5, "estimated_hours": 1, "dependencies": [1]
        }
        
        results = ScoringService.analyze_tasks([task_blocker, task_blocked])
        
        blocker_task = next(t for t in results if t['id'] == 1)
        blocked_task = next(t for t in results if t['id'] == 2)
        
        # Blocker should generally score higher due to dependency weight
        self.assertTrue(blocker_task['priority_score'] > blocked_task['priority_score'])
        self.assertIn("blocks 1 other tasks", blocker_task['rationale'])

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected and flagged"""
        # A depends on B, B depends on A
        task_a = {
            "id": 1, "title": "A", "dependencies": [2],
            "due_date": str(self.today), "importance": 5, "estimated_hours": 1
        }
        task_b = {
            "id": 2, "title": "B", "dependencies": [1],
            "due_date": str(self.today), "importance": 5, "estimated_hours": 1
        }
        
        results = ScoringService.analyze_tasks([task_a, task_b])
        
        for task in results:
            self.assertEqual(task['priority_score'], -1)
            self.assertEqual(task['rationale'], "Circular Dependency Detected!")
