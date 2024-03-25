var file_number = 20
var btn_get_next = document.getElementById('getNext')
var btn_run = document.getElementById('run')
var btn_stop = document.getElementById('stop')
var update_interval = 2000
btn_get_next.onclick = get_next_status
btn_run.onclick = run
btn_stop.onclick = stop_run

// variable to control timer, start-stop
var running_timer = 0;

// function to update statusoffline from, sends one request
function get_next_status(){
    clearInterval(running_timer)
    $.ajax({
        url: '',
        type: 'get',
        data: {
            // calls_counter : file_number,
        },
        // Do this in success
        success: function(response){
        update_status(response.machines)
        file_number++
        run()
        }
    })
}

// function for starting continuous process
function run(){
    running_timer = setInterval(function(){ get_next_status() }, update_interval);        
}

// function for stoping continuous process
function stop_run() {
  clearInterval(running_timer);
}

function parseTime(timeString){
    // Time string is in format HH:MM:SS
    var timeSegments = timeString.split(":");
    var hours = parseInt(timeSegments[0]);
    var minutes = parseInt(timeSegments[1]);
    var seconds = parseInt(timeSegments[2]);
    var totalSeconds = hours * 3600 + minutes * 60 + seconds;
    return totalSeconds;
}

// function to update status on the page
function update_status(machines){
    for (let machineName in machines){
        let machine = machines[machineName];
        let card = document.getElementById(machineName);
        card.getElementsByClassName('status')[0].innerHTML = machines[machineName].status
        card.getElementsByClassName('this_cycle_duration')[0].innerHTML = machines[machineName].this_cycle_duration
        
        let remainTimeElement = card.getElementsByClassName('remain_time')[0];
        remainTimeElement.innerHTML = machines[machineName].remain_time; // update 'remain_time' value here
        
        let lastCycleDurationElement = card.getElementsByClassName('last_cycle_duration')[0];
        lastCycleDurationElement.innerHTML = machines[machineName].last_cycle_duration;
        
        let remainTimeRowElement = card.getElementsByClassName('remain-time-row')[0]; // target the row element
        update_remain_time_visual(remainTimeRowElement, machines[machineName].remain_time, machines[machineName].last_cycle_duration); // update visual with the row element
        
        card.getElementsByClassName('current_machine_time')[0].innerHTML = machines[machineName].current_machine_time
        card.getElementsByClassName('current_tool')[0].innerHTML = machines[machineName].current_tool
        // Updates job
        // Attempt to find and update the corresponding job card
        let jobCardId = `${machineName}_active_job`;
        let jobCard = document.getElementById(jobCardId);
        if (jobCard) {
            // Assuming machine job data is structured as a dictionary in machine['active_job']
            let jobData = machine['active_job'];
            if(jobData){
                // Update each field in the job card
                jobCard.querySelector('div[name="active_job"]').textContent = `Active job: ${jobData.project}`;
                jobCard.querySelector('div[name="nc_program"]').textContent = `NC Program: ${jobData.nc_program}`;
                jobCard.querySelector('div[name="quantity"]').textContent = `Parts: ${jobData.currently_made_quantity} of ${jobData.required_quantity}`;
                jobCard.querySelector('div[name="cycle_time"]').textContent = `Cycle time: ${jobData.cycle_time}`;
                jobCard.querySelector('div[name="changing_time"]').textContent = `Changing time: ${jobData.part_changing_time}`;
                if (jobData.operation) {
                    jobCard.querySelector('div[name="operation"]').textContent = `Operation: ${jobData.operation} of ${jobData.operations_total}`;
                }
                jobCard.querySelector('div[name="started"]').textContent = `Started: ${jobData.started}`;
                jobCard.querySelector('div[name="finished"]').textContent = `Will end: ${jobData.will_end_at}`;
            }
        }
        update_visual()
    }
}


function update_remain_time_visual(remainTimeRowElement, remainTime, lastCycleTime){
    const maxTime = parseTime(lastCycleTime);
    const remainTimeSeconds = parseTime(remainTime);
    const timePassed = maxTime - remainTimeSeconds;
    const percentagePassed = (timePassed / maxTime) * 100;
    
    if(remainTimeSeconds > 0) {
        // This will set the color of the 'remain_time' row to be a solid green and orange, according to the percentage of time passed.
        remainTimeRowElement.style.background = `linear-gradient(90deg, green ${100-percentagePassed}%, orange ${100-percentagePassed}%)`;
    } else {
        // If remainTime is 0, make the entire row orange.
        remainTimeRowElement.style.background = 'orange';
    }
}



function update_job(machine, name){
    if (("is_part_made" in machine) && (machine['is_part_made'] == true)){
        // Update job card
        let card = document.getElementById(name + '_active_job')
        if (card !== null) {
            const reg = /\s\d+\s/g
            let current_value = parseInt(card.children[2].textContent.match(reg))
            current_value++
            updated_string = ' ' + current_value.toString() + ' '
            const updated_quantity = card.children[2].textContent.replace(reg, updated_string)
            card.children[2].textContent = updated_quantity
       }
    }
}

function update_visual(){
    const cards = document.getElementsByClassName('card-body')
    for (var i = 0; i < cards.length; i++){
        let card = cards[i]
        let status = cards[i].getElementsByClassName('status')[0].innerHTML
        if (status == 'STOPPED'){
        card.style.backgroundColor = "orange"
        if (status == 'FEED-HOLD'){
        card.style.backgroundColor = "blue"}
        } else if (status == 'ACTIVE'){
        card.style.backgroundColor = "green"}
    }
    }

update_visual()
run()
