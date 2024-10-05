// Immediately Invoked Function Expression to avoid polluting the global namespace
(function() {
  let medianTime; // This will be set once we have the job's time data
  let cycles; // To store cycles data globally for access in various functions
  let initialSetupTime; // Store initial setup time
  let currentScaleMinutes; // Globally store the current scale in minutes
  const MIN_CYCLE_WIDTH_PX = 3; // Minimum visual width for any cycle or gap in pixels

  // Event listener for DOM content loaded
  document.addEventListener('DOMContentLoaded', async function() {
    const timelineElement = document.getElementById('cycle-timeline-block');
    const timelineUrl = timelineElement.getAttribute('data-timeline-url');

    if (timelineUrl) {
      try {
        const data = await fetchTimelineData(timelineUrl);
        cycles = data.cycles; // Store cycles data globally
        initialSetupTime = data.initial_setup_time; // Store initial setup time
        setInitialMedianTime(data.job.started, data.job.ended);
        initializeSliderEventHandlers();
        setScaleSliderMaximum(cycles, document.getElementById('cycle-timeline-block').clientWidth);
        currentScaleMinutes = parseInt(document.getElementById('scale-slider').value, 10);
        updateTimes();
        renderCycleTimeline();
        displayMedianTime();
      } catch (error) {
        console.error('Failed to fetch cycle data:', error);
        timelineElement.textContent = 'Failed to load data';
      }
    } else {
      console.error('Timeline URL is not specified.');
      timelineElement.textContent = 'Timeline URL is not specified.';
    }
  });

  function initializeSliderEventHandlers() {
    const scaleSlider = document.getElementById('scale-slider');
    const scaleValueDisplay = document.getElementById('slider-value');
    const medianTimeSlider = document.getElementById('median-time-slider');

    scaleSlider.oninput = function() {
      currentScaleMinutes = parseInt(this.value, 10);
      scaleValueDisplay.textContent = currentScaleMinutes + ' minutes';
      updateTimes();
      renderCycleTimeline();
    };

    medianTimeSlider.oninput = function() {
      const medianMillis = parseInt(this.value, 10);
      medianTime = new Date(medianMillis);
      displayMedianTime();
      updateTimes();
      renderCycleTimeline();
    };

    setScaleSliderMaximum(cycles, document.getElementById('cycle-timeline-block').clientWidth);
    scaleSlider.value = scaleSlider.max;
    currentScaleMinutes = parseInt(scaleSlider.value, 10);
    scaleValueDisplay.textContent = currentScaleMinutes + ' minutes';
  }

  async function fetchTimelineData(url) {
    const response = await fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    if (!response.ok) throw new Error('Network response was not ok');
    return await response.json();
  }

  function setInitialMedianTime(start, end) {
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
    medianTime = endTime;
    const medianTimeSlider = document.getElementById('median-time-slider');
    medianTimeSlider.min = startTime.getTime();
    medianTimeSlider.max = endTime.getTime();
    medianTimeSlider.value = medianTimeSlider.max;
  }

  function setScaleSliderMaximum(cycles, timelineWidth) {
    const minDurationInSeconds = calculateMinimumCycleAndGapDuration(cycles);
    const minDurationInMinutes = minDurationInSeconds / 60;
    const maxScale = (minDurationInMinutes * timelineWidth) / MIN_CYCLE_WIDTH_PX;

    const scaleSlider = document.getElementById('scale-slider');
    scaleSlider.max = Math.floor(maxScale);
  }

  function calculateMinimumCycleAndGapDuration(cycles) {
    let minDurationInSeconds = Infinity;
    cycles.forEach(cycle => minDurationInSeconds = Math.min(minDurationInSeconds, cycle.duration));

    cycles.sort((a, b) => new Date(a.started) - new Date(b.started));
    for (let i = 0; i < cycles.length - 1; i++) {
      const gapInSeconds = (new Date(cycles[i + 1].started).getTime() - new Date(cycles[i].ended).getTime()) / 1000;
      if (gapInSeconds > 0) minDurationInSeconds = Math.min(minDurationInSeconds, gapInSeconds);
    }
    return minDurationInSeconds;
  }

  function timeToString(time) {
    const time_string = time.toISOString().replace('T', ' ').slice(0, 19);
    return time_string;
  }

  function displayMedianTime() {
    const medianTimeElement = document.getElementById('median-time');
    medianTimeElement.textContent = timeToString(medianTime);
  }

  function updateTimes() {
    const halfScaleMillis = currentScaleMinutes * 60000 / 2;
    const newStartTime = new Date(medianTime.getTime() - halfScaleMillis);
    const newEndTime = new Date(medianTime.getTime() + halfScaleMillis);

    document.getElementById('start-time').textContent = newStartTime.toISOString().replace('T', ' ').slice(0, 19);
    document.getElementById('end-time').textContent = newEndTime.toISOString().replace('T', ' ').slice(0, 19);
  }

  function renderCycleTimeline() {
    const timeline = document.getElementById('cycle-timeline-block');
    const visibleStartTime = new Date(medianTime.getTime() - (currentScaleMinutes * 60000 / 2));
    const visibleEndTime = new Date(medianTime.getTime() + (currentScaleMinutes * 60000 / 2));

    timeline.innerHTML = ''; // Clear any existing content
    const baseLine = document.createElement('div');
    baseLine.className = 'base-timeline';
    timeline.appendChild(baseLine);

    // Render initial setup time
    if (initialSetupTime) {
        renderInitialSetupTime(initialSetupTime, visibleStartTime, visibleEndTime);
    }

    renderChangingTimes(cycles, visibleStartTime, visibleEndTime);

    cycles.forEach(cycle => {      
        const { adjustedStart, adjustedEnd } = adjustCycleVisibility(cycle, visibleStartTime, visibleEndTime);
        if (new Date(cycle.started) <= visibleEndTime && new Date(cycle.ended) >= visibleStartTime) {
            // Check if the cycle is a setup cycle
            if (cycle.is_setup) {
                const setupDiv = document.createElement('div');
                setupDiv.id = `cycle-${cycle.id}`; // Assign a unique ID based on cycle id
                setupDiv.className = 'setup on-bottom';
                setupDiv.setAttribute('data-cycle-info', JSON.stringify({
                    id: cycle.id,
                    tool_sequence: cycle.tool_sequence,
                    is_full_cycle: cycle.is_full_cycle,
                    is_setup: cycle.is_setup,
                    is_warmup: cycle.is_warm_up,
                    started: cycle.started,
                    ended: cycle.ended,
                    duration: cycle.duration,
                    changing_time: cycle.changing_time
                }));
                setupDiv.addEventListener('mouseenter', () => updateTooltipContent(cycle));
                setupDiv.addEventListener('mouseleave', () => clearTooltipContent());
                positionCycleDiv(setupDiv, adjustedStart.toISOString(), adjustedEnd.toISOString(), visibleStartTime.toISOString(), visibleEndTime.toISOString());
                timeline.appendChild(setupDiv);
            } else {
                const cycleDiv = document.createElement('div');
                cycleDiv.id = `cycle-${cycle.id}`; // Assign a unique ID based on cycle id
                cycleDiv.className = 'cycle on-top';
                cycleDiv.setAttribute('data-cycle-info', JSON.stringify({
                    id: cycle.id,
                    tool_sequence: cycle.tool_sequence,
                    is_full_cycle: cycle.is_full_cycle,
                    is_setup: cycle.is_setup,
                    is_warmup: cycle.is_warm_up,
                    started: cycle.started,
                    ended: cycle.ended,
                    duration: cycle.duration,
                    changing_time: cycle.changing_time
                }));
                cycleDiv.addEventListener('mouseenter', () => updateTooltipContent(cycle));
                cycleDiv.addEventListener('mouseleave', () => clearTooltipContent());
                positionCycleDiv(cycleDiv, adjustedStart.toISOString(), adjustedEnd.toISOString(), visibleStartTime.toISOString(), visibleEndTime.toISOString());
                timeline.appendChild(cycleDiv);
            }
        }
    });
  }

  function renderInitialSetupTime(initialSetupTime, visibleStartTime, visibleEndTime) {
    const timeline = document.getElementById('cycle-timeline-block');
    const { adjustedStart, adjustedEnd } = adjustCycleVisibility({
        started: initialSetupTime.started,
        ended: initialSetupTime.ended
    }, visibleStartTime, visibleEndTime);

    if (adjustedStart < visibleEndTime && adjustedEnd > visibleStartTime) {
        const initialSetupDiv = document.createElement('div');
        initialSetupDiv.className = 'initial-setup on-bottom';
        positionCycleDiv(initialSetupDiv, adjustedStart.toISOString(), adjustedEnd.toISOString(), visibleStartTime.toISOString(), visibleEndTime.toISOString());
        timeline.appendChild(initialSetupDiv);
    }
  }

  function renderChangingTimes(cycles, visibleStartTime, visibleEndTime) {
    const timeline = document.getElementById('cycle-timeline-block');

    cycles.forEach(cycle => {
        const changingStartTime = new Date(new Date(cycle.started).getTime() - cycle.changing_time * 1000);
        const changingEndTime = new Date(cycle.started);

        const { adjustedStart, adjustedEnd } = adjustCycleVisibility({
            started: changingStartTime.toISOString(),
            ended: changingEndTime.toISOString()
        }, visibleStartTime, visibleEndTime);

        if (adjustedStart < visibleEndTime && adjustedEnd > visibleStartTime) {
            const changingTimeDiv = document.createElement('div');
            changingTimeDiv.className = 'changing-time on-top';
            positionCycleDiv(changingTimeDiv, adjustedStart.toISOString(), adjustedEnd.toISOString(), visibleStartTime.toISOString(), visibleEndTime.toISOString());
            timeline.appendChild(changingTimeDiv);
        }
    });
  }

  function updateTooltipContent(cycle) {
    updateTooltipText('tooltip-start', `Start: ${timeToString(new Date(cycle.started))}`);
    updateTooltipText('tooltip-end', `End: ${timeToString(new Date(cycle.ended))}`);
    updateTooltipText('tooltip-id', `ID: ${cycle.id}`);
  }

  function updateTooltipText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
  }

  function clearTooltipContent() {
    updateTooltipText('tooltip-start', 'Start: N/A');
    updateTooltipText('tooltip-end', 'End: N/A');
    updateTooltipText('tooltip-id', 'ID: N/A');
  }

  function adjustCycleVisibility(cycle, visibleStartTime, visibleEndTime) {
    let adjustedStart = new Date(cycle.started);
    let adjustedEnd = new Date(cycle.ended);

    if (adjustedStart < visibleStartTime) {
        adjustedStart = visibleStartTime;
    }

    if (adjustedEnd > visibleEndTime) {
        adjustedEnd = visibleEndTime;
    }

    return { adjustedStart, adjustedEnd };
  }

  function positionCycleDiv(div, start, end, timelineStart, timelineEnd) {
    const startDate = new Date(start).getTime();
    const endDate = new Date(end).getTime();
    const timelineStartDate = new Date(timelineStart).getTime();
    const timelineEndDate = new Date(timelineEnd).getTime();
    const timelineDuration = timelineEndDate - timelineStartDate;
    const startOffset = (startDate - timelineStartDate) / timelineDuration;
    const duration = (endDate - startDate) / timelineDuration;

    div.style.left = `${startOffset * 100}%`;
    div.style.width = `${duration * 100}%`;

    if (div.classList.contains('on-top')) {
        div.style.top = '50%'; // Align with the top of the base timeline
        div.style.transform = 'translateY(-100%)'; // Adjust to place it above the base timeline
    } else if (div.classList.contains('on-bottom')) {
        div.style.top = '50%'; // Align with the bottom of the base timeline
        div.style.transform = 'translateY(0%)'; // Adjust to place it below the base timeline
    }
}

  function positionChangingTimeDiv(div, start, end, timelineStart, timelineEnd) {
    const startDate = new Date(start).getTime();
    const endDate = new Date(end).getTime();
    const timelineStartDate = new Date(timelineStart).getTime();
    const timelineEndDate = new Date(timelineEnd).getTime();
    const timelineDuration = timelineEndDate - timelineStartDate;
    const startOffset = (startDate - timelineStartDate) / timelineDuration;
    const duration = (endDate - startDate) / timelineDuration;
  
    div.style.left = `${startOffset * 100}%`;
    div.style.width = `${duration * 100}%`;
    div.style.top = '50%';
    div.style.transform = 'translateY(0%)'; // Adjust to place it below the base timeline
  }

})();
