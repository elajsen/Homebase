$(document).ready(function(){
    const current_url = window.location.href
    const current_page = current_url.split("/")[current_url.split("/").length - 1]
    console.log("CURRENT PAGE", current_page)

    if (current_page == "budget"){
        const spending_graph = document.getElementById('spending-graph-canvas');
        const income_graph = document.getElementById('income-graph-canvas');

        const spending_graph_data = getSpendingGraphData()
        const income_graph_data = getIncomeGraphData()

        getGraph(spending_graph,
            "doughnut",
            "€",
            spending_graph_data["labels"],
            spending_graph_data["data"])
        getGraph(income_graph,
            "doughnut",
            "€",
            income_graph_data["labels"],
            income_graph_data["data"])
    } else if (current_page == "monthly_recap"){
        console.log("Correct graph else")
        $(".graph-canvas").map(function(){
            const graph_name = $(this).attr("name")

            const raw_data = $("#graph-data-" + graph_name).attr("data")
            const raw_diff = $("#graph-diff-" + graph_name).attr("data")
            console.log(raw_diff)
            const raw_label = $("#graph-labels-" + graph_name).attr("data")

            const data = JSON.parse(raw_data.replace(/'/g, '"'))
            const diff = JSON.parse(raw_diff.replace(/'/g, '"'))
            console.log(diff)
            const label = JSON.parse(raw_label.replace(/'/g, '"'))

            data.reverse();
            label.reverse();
            diff.reverse();

            const graph_canvas = $("#graph-canvas-" + graph_name)

            getDualGraph(graph_canvas,
                "line",
                "€",
                label,
                [data, diff])
        })
    }
    
})

function getSpendingGraphData(){
    let labels = []
    let data = []

    $(".spending_icons").map(function(){
        labels.push($(this).attr("title"))
    });

    $(".spending-amount").map(function(){
        data.push($(this).html().replace("€", ""))
    });

    var return_dict = {
        "labels": labels,
        "data": data
    };
    //console.log(return_dict)
    return return_dict
}

function getIncomeGraphData(){
    let labels = []
    let data = []

    $(".income_icons").map(function(){
        labels.push($(this).attr("title"))
    });

    $(".income-amount").map(function(){
        data.push($(this).html().replace("€", ""))
    });

    var return_dict = {
        "labels": labels,
        "data": data
    };
    //console.log(return_dict)
    return return_dict
}

function getGraph(object, type, unit_label, labels, data){
    new Chart(object, {
        type: type,
        data: {
        labels: labels,
        datasets: [{
            label: unit_label,
            data: data,
            backgroundColor:[
                "rgb(182, 203, 158)",
                'rgb(146, 180, 167)',
                'rgb(209, 240, 177)',
                'rgb(140, 138, 147)',
            ],
            hoverOffset: 4
        }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
            chartOptions: {
                responsive: true,
                responsivenes: true,
                maintainAspectRatio: true,
            }
        }
    });
}

function getDualGraph(object, type, unit_label, labels, data){
    new Chart(object, {
        type: type,
        data: {
        labels: labels,
        datasets: [{
            label: unit_label,
            data: data[0],
            borderColor: "rgb(182 203 158)", 
            backgroundColor:[
                "rgb(182, 203, 158)",
                'rgb(146, 180, 167)',
                'rgb(209, 240, 177)',
                'rgb(140, 138, 147)',
            ],
            hoverOffset: 4,
            yAxisID:"amount"
        },
        {
            label: "%",
            data: data[1],
            borderColor: "rgb(250, 0, 0)",
            backgroundColor:[
                "rgb(250, 0, 0)",
            ],
            hoverOffset: 4,
            yAxisID:"diff"
        }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
            chartOptions: {
                responsive: true,
                responsivenes: true,
                maintainAspectRatio: true,
            },
            scales: {
                amount: {
                    type: "linear",
                    display: true,
                    position: "left"
                },
                diff: {
                    type: "linear",
                    display: true,
                    position: "right"
                }
            }
        }
    });
}