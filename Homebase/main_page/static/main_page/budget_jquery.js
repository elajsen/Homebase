function update_amounts(){
    const total_spending = $("#budget_table_row").attr("total_spending")
    const salary = $("#budget_salary").val()
    const savings = $("#budget_savings").val()

    const new_net = Number((salary - total_spending - savings).toFixed(2))

    const days = $(".budget_week_modal").map(function() {
        return Number(this.getAttribute("remaining_days"));
    }).get();

    const total_days = days.reduce((partialSum, a) => partialSum + a, 0);

    $(".budget_week_modal").map(function() {
        var new_amount = Number(((new_net / total_days) * this.getAttribute("remaining_days")).toFixed(2))
        var week = $(this).attr("id").split("_")[2]

        $("#week_amount_" + week).html("€" + new_amount)
    });
}

$(document).ready(function(){
    $("#budget_savings").on("input", function() {
        update_amounts();
    });
    $("#budget_salary").on("input", function() {
        update_amounts();
    });
})
