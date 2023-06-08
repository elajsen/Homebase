$(document).ready(function(){
    const spending_graph = document.getElementById('spending-graph-canvas');
    const income_graph = document.getElementById('income-graph-canvas');

    const spending_graph_data = getSpendingGraphData()
    const income_graph_data = getIncomeGraphData()

    getGraph(spending_graph, spending_graph_data["labels"], spending_graph_data["data"])
    getGraph(income_graph, income_graph_data["labels"], income_graph_data["data"])
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
    console.log(return_dict)
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
    console.log(return_dict)
    return return_dict
}

function getGraph(object, labels, data){
    new Chart(object, {
        type: 'doughnut',
        data: {
        labels: labels,
        datasets: [{
            label: '€',
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
            }
        }
    });
}