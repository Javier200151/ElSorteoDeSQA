document.getElementById("fetchTopics").addEventListener("click", function () {
    fetch("/api/get_topics")
        .then(response => response.json())
        .then(data => {
            // Llena las listas con los datos de los topics
            const selects = ["partida1", "partida2", "partida3", "partida_jugar"];
            selects.forEach(id => {
                const select = document.getElementById(id);
                select.innerHTML = "";
                data.forEach(topic => {
                    const option = document.createElement("option");
                    option.value = topic.id;
                    option.textContent = topic.title;
                    select.appendChild(option);
                });
            });
        });
});

document.getElementById("runLottery").addEventListener("click", function () {
    const premios = ["Premio 1", "Premio 2", "Premio 3"];
    const jugadores_papeletas = { "Jugador1": 4, "Jugador2": 2, "Jugador3": 0 };
    fetch("/api/run_lottery", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jugadores_papeletas, premios })
    })
    .then(response => response.json())
    .then(data => {
        const resultsTable = document.getElementById("results");
        resultsTable.innerHTML = "<tr><th>Premio</th><th>Ganador</th></tr>";
        Object.entries(data).forEach(([premio, ganador]) => {
            const row = `<tr><td>${premio}</td><td>${ganador}</td></tr>`;
            resultsTable.innerHTML += row;
        });
    });
});