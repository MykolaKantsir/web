document.addEventListener('DOMContentLoaded', function() {
    const cycleTimelineBlock = document.getElementById('cycle-timeline-block');
    let selectedCycles = [];

    cycleTimelineBlock.addEventListener('click', function(event) {
        const target = event.target;
        // Check for both regular cycles and setup cycles
        if (target.classList.contains('cycle') || target.classList.contains('setup')) {
            toggleCycleSelection(target);
        }
    });

    document.getElementById('combine-cycles').addEventListener('click', function() {
        if (selectedCycles.length === 2) {
            combineTwoCycles(selectedCycles[0], selectedCycles[1]);
        }
    });

    document.getElementById('deselect-cycles').addEventListener('click', function() {
        deselectAllCycles();
    });

    function toggleCycleSelection(cycleDiv) {
        const id = cycleDiv.id;
        const isSelected = cycleDiv.classList.contains('selected');
        if (isSelected) {
            cycleDiv.classList.remove('selected');
            selectedCycles = selectedCycles.filter(selectedId => selectedId !== id);
        } else {
            if (selectedCycles.length < 2) {
                cycleDiv.classList.add('selected');
                selectedCycles.push(id);
            }
        }
        updateCycleInfoDisplay();
        updateInteractionBlockVisibility();
    }

    function updateCycleInfoDisplay() {
        selectedCycles.forEach((id, index) => {
            const cycleDiv = document.getElementById(id);
            const cycleData = JSON.parse(cycleDiv.getAttribute('data-cycle-info')); // Ensure data-cycle-info is set on each cycle div
            document.getElementById(`cycle-id-${index+1}`).textContent = `ID: ${cycleData.id}`;
            document.getElementById(`cycle-tool-sequence-${index+1}`).textContent = `Tool Sequence: ${cycleData.tool_sequence}`;
            document.getElementById(`cycle-is-full-cycle-${index+1}`).textContent = `Is Full Cycle: ${cycleData.is_full_cycle}`;
            document.getElementById(`cycle-is-setup-${index+1}`).textContent = `Is Setup: ${cycleData.is_setup}`;
        });

        for (let i = selectedCycles.length + 1; i <= 2; i++) {
            document.getElementById(`cycle-id-${i}`).textContent = `ID: N/A`;
            document.getElementById(`cycle-tool-sequence-${i}`).textContent = `Tool Sequence: N/A`;
            document.getElementById(`cycle-is-full-cycle-${i}`).textContent = `Is Full Cycle: N/A`;
            document.getElementById(`cycle-is-setup-${i}`).textContent = `Is Setup: N/A`;
        }

        document.getElementById('combine-cycles').disabled = selectedCycles.length !== 2;
    }

    function deselectAllCycles() {
        selectedCycles.forEach(id => {
            const cycleDiv = document.getElementById(id);
            if (cycleDiv) {
                cycleDiv.classList.remove('selected');
            }
        });
        selectedCycles = [];
        updateCycleInfoDisplay();
        updateInteractionBlockVisibility();
    }

    function updateInteractionBlockVisibility() {
        const interactionBlock = document.getElementById('cycle-interaction-block');
        interactionBlock.style.display = selectedCycles.length > 0 ? 'block' : 'none';
    }
});
