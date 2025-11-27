# Smart Task Analyzer

Hi! This is my submission for the Software Development Intern position. I've built a a mini-application that intelligently scores and prioritizes tasks based on multiple factors.

## Setup Instructions

Getting the project running is straightforward:

1.  **Backend (Django)**

    ```bash
    cd backend

    # Create and activate virtual environment (Recommended)
    python -m venv venv
    
    # Mac/Linux:
    source venv/bin/activate

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```

2.  **Frontend**
    - Just open `frontend/index.html` in any web browser.
    - It connects to `http://127.0.0.1:8000` by default.

## Algorithm Explanation

I spent a good amount of time refining the `ScoringService` to make the prioritization feel "human". Here is the logic behind each factor:

1.  **Urgency (Weight: 1.5)**

    - _Logic_: I used a non-linear approach here. Tasks due today get a flat 100 points. Overdue tasks get 100 points plus 5 points for every day they are late (increasing pressure). Future tasks decay rapidly (`100 / (days + 1)`), so something due in a month barely impacts the score compared to something due tomorrow.

2.  **Importance (Weight: 1.2)**

    - _Logic_: This is a direct mapping of the user's intent. I multiply the 1-10 rating by 10 to normalize it to a 0-100 scale. This ensures that a "High Importance" task always has a strong baseline score.

3.  **Effort (Weight: 0.8)**

    - _Logic_: I wanted to prioritize "Quick Wins". The score is calculated as `100 / estimated_hours`. This means a 30-minute task gets a massive score boost, encouraging users to clear their plate of small items, while massive 10-hour projects rely on their Importance/Urgency scores to rank high.

4.  **Dependencies (Weight: 2.0)**
    - _Logic_: Unblocking others is critical in any team. For every task that a specific task blocks, it receives a +30 point bonus. If Task A blocks 3 other tasks, it gets a huge 90-point boost, likely pushing it to the top of the list.

**Cycle Detection**: Before any scoring happens, I run a Depth-First Search (DFS) to catch circular dependencies (e.g., A waits for B, B waits for A). If detected, I flag these with a score of `-1` so the user sees them immediately as errors.

## Design Decisions

- **Stateless `/analyze` Endpoint**: I decided to make the main analysis endpoint stateless. The frontend sends the JSON, and the backend processes it without saving to the DB. This allows users to play with "what-if" scenarios (changing dates, importance) instantly without cluttering the database with draft tasks.
- **Client-Side Sorting**: While the backend does the heavy lifting for the "Smart" score, I implemented the "Fastest", "Impact", and "Deadline" sorts in JavaScript. This makes the UI feel instant when toggling views, as we don't need to hit the server again.
- **DFS for Cycles**: I chose DFS over other graph algorithms because it's efficient ($O(V+E)$) and easy to implement recursively for this specific problem size.

## Time Breakdown

- **Backend (Models & Views)**: ~45 mins - Setting up Django and the basic API structure.
- **Algorithm Design**: ~2 hours - Tuning the weights and writing the cycle detection logic.
- **Frontend**: ~1.5 hours - Building the UI and handling the dynamic API responses.
- **Testing & Polish**: ~1.5 hours - Writing unit tests and this documentation.

## Bonus Challenges Attempted

- **Dependency Graph**: I implemented the backend logic to detect and flag circular dependencies.
- **Unit Tests**: I wrote comprehensive tests (`backend/tasks/tests.py`) to verify the scoring logic and cycle detection.

Thanks for reviewing my code!
