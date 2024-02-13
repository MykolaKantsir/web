var machine_cards = document.getElementsByName("machine_container")
var machines_container = document.getElementById("machines_container")
const machine_cards_per_row = 3
for (let counter=0; counter < machine_cards.length; counter++){
    if (counter % machine_cards_per_row === 0){
        let machine_row = document.createElement("div")
        machine_row.className = "row"
        machine_row.style.marginTop = "30px"
        for (let machine_column_counter=0; machine_column_counter < machine_cards_per_row; machine_column_counter++){
            let machine_column = document.createElement("div")
            machine_column.className = "col"
            let card = machine_cards[0]
            machine_column.append(card)
            machine_row.append(machine_column)
        }
        machines_container.append(machine_row)
        
    }
}