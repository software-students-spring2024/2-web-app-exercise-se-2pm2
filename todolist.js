document.addEventListener('DOMContentLoaded', function() {
    var calendarElement = new document.getElementById('calendar');
    if (!calendarElement) {
        console.error("Calendar element not found.");
        return;
    }
    var calendar = new FullCalendar.Calendar(calendarElement, {
        initialView: 'dayGridMonth',
        selectable: true,
        dateClick: function(info) {
            $('#date').val(info.dateStr); 
        }
    });
    calendar.render();

    getTask(); 
});
document.addEventListener("DOMContentLoaded", function() {
document.getElementById("todo-form").addEventListener("submit", function(){
    const taskInput = document.getElementById("todo-input").ariaValueMax;
    const dateInput = $('#date').val()
    addTask(dateInput, taskInput)
});
});

async function getTask() {
        try {
            const response = await fetch("/get_task")
            const tasks = await response.json();
            const taskList = document.getElementById("get-task");
            taskList.innerHTML = "";
            tasks.forEach(tasks=>{
            const item = document.createElement("li");
            item.textContent = task.dateInput + " " + task.taskInput;
            taskList.appendChild(item);
        })
    }catch(error){
        console.error("Error:", error);
    }
}
    
           
async function addTask(taskInput) {
    try {
        const response = await fetch("/add_task", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ date: dateInput, task: taskInput })
        });

        if (response.ok) {
            console.log("Task added successfully!");
        } else {
            console.error("Failed to add task.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}
