import datetime 
from datetime import date 
from typing import List, Dict, Any, Set

class ScoringService:
    WEIGHTS = {
        'urgency': 1.5,
        'importance': 1.2,
        'effort': 0.8,
        'dependency': 2.0
    }
    
    @staticmethod
    def calculateScore(task: Dict[str, Any], all_tasks_map: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        score = 0
        rationales = []
        today = date.today()
        due_date_value = task.get('due_date')
        due_date = None

        if isinstance(due_date_value, date):
            due_date = due_date_value
        elif isinstance(due_date_value, str) and due_date_value:
            try:
                due_date = datetime.datetime.strptime(due_date_value, "%Y-%m-%d").date()
            except ValueError:
                due_date = None

        if due_date:
            days_remaining = (due_date - today).days

            if days_remaining < 0:
                urgency_score = 100 + abs(days_remaining) * 5
                rationales.append(f"Overdue by {abs(days_remaining)} days")
            elif days_remaining == 0:
                urgency_score = 100
                rationales.append("Due today")
            else:
                urgency_score = 100 / (days_remaining + 1)
        else:
            urgency_score = 0  # default 0 to be made dynamic later
        score += urgency_score * ScoringService.WEIGHTS['urgency']
        
        importance = task.get('importance', 5)  # default 5 to be made dynamic later
        importance_score = importance * 10
        score += importance_score * ScoringService.WEIGHTS['importance']
        
        if importance >= 8:
            rationales.append("High importance")
        
        hours = task.get('estimated_hours', 2)  # default 2 to be made dynamic later
        hours = max(hours, 0.5)  # for capping the effort score
        effort_score = 100 / hours
        score += effort_score * ScoringService.WEIGHTS['effort']
        
        if hours < 2:
            rationales.append("Quick Win")
        
        task_id = task.get('id')
        blocked_tasks_count = 0
        
        if task_id:
            for other_task in all_tasks_map.values():
                if task_id in other_task.get('dependencies', []):
                    blocked_tasks_count += 1
        dependency_score = blocked_tasks_count * 30  # to be made dynamic like avg of all other tasks
        score += dependency_score * ScoringService.WEIGHTS['dependency']
        
        if blocked_tasks_count > 0:
            rationales.append(f"blocks {blocked_tasks_count} other tasks")
        
        task['priority_score'] = round(score, 2)
        task['rationale'] = " | ".join(rationales)
        return task
    
    @staticmethod
    def detect_cycle(tasks: List[Dict[str, Any]]) -> Set[int]:
        adj_list = {t['id']: t.get('dependencies', []) for t in tasks if 'id' in t}
        circular_ids = set()
        
        for start_node in adj_list:
            visited = set()
            recursion_stack = set()
            
            def dfs(node_id):
                visited.add(node_id)
                recursion_stack.add(node_id)
                
                for neighbor in adj_list.get(node_id, []):
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in recursion_stack:
                        return True
                recursion_stack.remove(node_id)
                return False

            if dfs(start_node):
                circular_ids.add(start_node)
        return circular_ids
    
    @staticmethod
    def analyze_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks_map = {t.get('id'): t for t in tasks}
        circular_ids = ScoringService.detect_cycle(tasks)
        processed_tasks = []
        
        for task in tasks:
            if task.get('id') in circular_ids:
                task['priority_score'] = -1
                task['rationale'] = "Circular Dependency Detected!"
                processed_tasks.append(task)
                continue
            scored_task = ScoringService.calculateScore(task, tasks_map)
            processed_tasks.append(scored_task)
        
        return sorted(processed_tasks, key=lambda x: x['priority_score'], reverse=True)