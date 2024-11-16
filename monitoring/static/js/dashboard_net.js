// Function to format ISO 8601 duration (P0DT00H00M00S) to HH:MM:SS format
function formatDuration(duration) {
    const matches = duration.match(/P(?:\d+D)?T(\d+H)?(\d+M)?(\d+S)?/);
    if (!matches) return "00:00:00";

    const hours = parseInt(matches[1]) || 0;
    const minutes = parseInt(matches[2]) || 0;
    const seconds = parseInt(matches[3]) || 0;

    return String(hours).padStart(2, '0') + ":" +
           String(minutes).padStart(2, '0') + ":" +
           String(seconds).padStart(2, '0');
}

// Function to parse HH:MM:SS time format into total seconds
function parseTime(timeString) {
    const [hours, minutes, seconds] = timeString.split(":").map(Number);
    return hours * 3600 + minutes * 60 + seconds;
}

// Function to update the visual background of the remain time row based on time passed
function update_remain_time_visual(remainTimeRowElement, remainTime, lastCycleTime) {
    // Check if time values are valid before updating the visual
    if (!remainTimeRowElement || remainTime === "loading" || lastCycleTime === "loading") return;

    const maxTime = parseTime(lastCycleTime);
    const remainTimeSeconds = parseTime(remainTime);
    const timePassed = maxTime - remainTimeSeconds;
    const percentagePassed = (timePassed / maxTime) * 100;

    if (remainTimeSeconds > 0) {
        remainTimeRowElement.style.background = `linear-gradient(90deg, green ${100 - percentagePassed}%, orange ${100 - percentagePassed}%)`;
    } else {
        remainTimeRowElement.style.background = 'orange';
    }
}

// Function to fetch the latest machine states from the server
function fetchMachineStates() {
    fetch('/monitoring/dashboard/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => updateMachineCards(data.machines))
    .catch(error => console.error('Error fetching machine states:', error));
}

// Function to update the content of each machine card
function updateMachineCards(machines) {
    for (const [machineName, state] of Object.entries(machines)) {
        const card = document.getElementById(`machine_${machineName}`);
        if (card) {
            // Update text fields
            card.querySelector('.status').textContent = state.status || 'loading';
            card.querySelector('.this_cycle_duration').textContent = formatDuration(state.this_cycle_duration) || 'loading';
            card.querySelector('.remain_time').textContent = formatDuration(state.remain_time) || 'loading';
            card.querySelector('.last_cycle_duration').textContent = formatDuration(state.last_cycle_duration) || 'loading';
            card.querySelector('.current_tool').textContent = state.current_tool || 'loading';
            card.querySelector('.active_nc_program').textContent = state.active_nc_program || 'loading';
            card.querySelector('.current_machine_time').textContent = formatDuration(state.current_machine_time) || 'loading';

            // Update remaining time visual if valid times are present
            const remainTimeRowElement = card.querySelector('.remain-time-row');
            if (state.remain_time && state.last_cycle_duration) {
                update_remain_time_visual(remainTimeRowElement, state.remain_time, state.last_cycle_duration);
            }
        }
    }

    // Update card background colors based on status
    update_visual();
}

// Function to update the card background color based on machine status
function update_visual() {
    const cards = document.getElementsByClassName('card-body');
    for (let card of cards) {
        const status = card.querySelector('.status').textContent;
        let backgroundColor = "";
        let textColor = "black"; // Default text color

        if (status === 'STOPPED') {
            backgroundColor = "orange";
            textColor = "white";
        } else if (status === 'FEED-HOLD') {
            backgroundColor = "blue";
            textColor = "white";
        } else if (status === 'ACTIVE') {
            backgroundColor = "green";
            textColor = "white";
        } else if (status === 'ALARM') {
            backgroundColor = "red";
            textColor = "white";
        }

        // Set the background color of the card
        card.style.backgroundColor = backgroundColor;

        // Set the text color for all relevant elements within the card
        const textElements = card.querySelectorAll('.status, .this_cycle_duration, .remain_time, .last_cycle_duration, .current_tool, .active_nc_program, .current_machine_time');
        textElements.forEach(element => {
            element.style.color = textColor;
        });
    }
}

// Function to start the periodic fetching of machine states every 30 seconds
function startFetching() {
    fetchMachineStates();  // Initial fetch
    setInterval(fetchMachineStates, 2000);  // Fetch every 2 seconds
}

// Start fetching machine states once the page has fully loaded
document.addEventListener('DOMContentLoaded', startFetching);
