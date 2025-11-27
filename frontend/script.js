let tasks = [];
let analyzedTasks = [];

function switchTab(tabName) {
  document
    .querySelectorAll(".tab-content")
    .forEach((el) => el.classList.remove("active"));
  document
    .querySelectorAll(".tab-btn")
    .forEach((el) => el.classList.remove("active"));

  document.getElementById(`${tabName}-tab`).classList.add("active");
  const buttons = document.querySelectorAll(".tab-btn");
  if (tabName === "form") buttons[0].classList.add("active");
  else buttons[1].classList.add("active");
}

document.getElementById("task-form").addEventListener("submit", (e) => {
  e.preventDefault();

  const task = {
    id: parseInt(document.getElementById("task_id").value) || Date.now(),
    title: document.getElementById("title").value,
    due_date: document.getElementById("due_date").value || null,
    estimated_hours: parseFloat(
      document.getElementById("estimated_hours").value
    ),
    importance: parseInt(document.getElementById("importance").value),
    dependencies: document
      .getElementById("dependencies")
      .value.split(",")
      .map((id) => parseInt(id.trim()))
      .filter((id) => !isNaN(id)),
  };

  tasks.push(task);
  updateCount();
  e.target.reset();
  document.getElementById("estimated_hours").value = 1;
  document.getElementById("importance").value = 5;
  alert("Task added to list!");
});

function loadJson() {
  try {
    const input = document.getElementById("json-input").value;
    const parsed = JSON.parse(input);
    if (Array.isArray(parsed)) {
      tasks = parsed;
      updateCount();
      alert(`Loaded ${tasks.length} tasks from JSON`);
    } else {
      alert("Input must be a JSON array");
    }
  } catch (e) {
    alert("Invalid JSON format");
  }
}

function updateCount() {
  document.getElementById("task-count").innerText = tasks.length;
}

function clearTasks() {
  tasks = [];
  analyzedTasks = [];
  updateCount();
  document.getElementById("results-list").innerHTML = "";
}

async function analyzeTasks() {
  if (tasks.length === 0) {
    alert("Add tasks first!");
    return;
  }

  const btn = document.querySelector(".btn.primary");
  const originalText = btn.innerText;
  btn.innerText = "Analyzing...";
  btn.disabled = true;

  try {
    const response = await fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(tasks),
    });

    if (!response.ok) throw new Error("API Error");

    analyzedTasks = await response.json();
    renderTasks();
  } catch (error) {
    console.error(error);
    alert(
      "Failed to analyze tasks. Ensure backend is running at http://127.0.0.1:8000"
    );
  } finally {
    btn.innerText = originalText;
    btn.disabled = false;
  }
}

function renderTasks() {
  const container = document.getElementById("results-list");
  const strategy = document.getElementById("sort-strategy").value;

  if (analyzedTasks.length === 0) {
    container.innerHTML =
      '<p style="text-align:center; color:#666;">No results yet.</p>';
    return;
  }

  let displayTasks = [...analyzedTasks];

  if (strategy === "fastest") {
    displayTasks.sort((a, b) => a.estimated_hours - b.estimated_hours);
  } else if (strategy === "impact") {
    displayTasks.sort((a, b) => b.importance - a.importance);
  } else if (strategy === "deadline") {
    displayTasks.sort((a, b) => {
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return new Date(a.due_date) - new Date(b.due_date);
    });
  } else {
    displayTasks.sort((a, b) => b.priority_score - a.priority_score);
  }

  container.innerHTML = displayTasks
    .map((task) => {
      let priorityClass = "priority-low";
      if (task.priority_score > 50) priorityClass = "priority-medium";
      if (task.priority_score > 100) priorityClass = "priority-high";
      if (task.priority_score === -1) priorityClass = "priority-high"; // Circular dependency

      return `
            <div class="task-card ${priorityClass}">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <div class="task-score">Score: ${task.priority_score}</div>
                </div>
                <div class="task-meta">
                    Due: ${task.due_date || "None"} | 
                    Hours: ${task.estimated_hours} | 
                    Imp: ${task.importance}/10
                </div>
                <div class="task-rationale">
                    ${task.rationale || "No specific rationale"}
                </div>
            </div>
        `;
    })
    .join("");
}
