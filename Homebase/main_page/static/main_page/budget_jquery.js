function update_amounts(){
    const total_spending = $("#budget-modal-section").attr("total_spending")
    const salary = $("#budget_salary").val()
    const savings = $("#budget_savings").val()

    const new_net = Number((salary - total_spending - savings).toFixed(2))

    const days = $(".budget_modal").map(function() {
        return Number(this.getAttribute("remaining_days"));
    }).get();

    const total_days = days.reduce((partialSum, a) => partialSum + a, 0);

    $(".budget_modal").map(function() {
        var new_amount = Number(((new_net / total_days) * this.getAttribute("remaining_days")).toFixed(2))
        var week = $(this).attr("id").split("_")[1]
        $("#week_amount_" + week).html("€" + new_amount)
    });
}

function handle_bills(){
    value = $("#budget-remove-checkbox").is(":checked");
    let bill_amounts = 0

    $(".bill-amount").map(function(){
        let amt = $(this).html()
        bill_amounts += Number(amt.replace("€", ""))
    });

    let total_amount = Number(Number($("#budget-modal-section").attr("total_spending")).toFixed(2))

    if (!value){
        bill_amounts *= -1
    }

    let new_total_amount = total_amount + Number(bill_amounts.toFixed(2))
    $("#budget-modal-section").attr("total_spending", new_total_amount)
    update_amounts()
}

$(document).ready(function(){
    $("#budget_savings").on("input", function() {
        update_amounts();
    });
    $("#budget_salary").on("input", function() {
        update_amounts();
    });
    $("#budget-remove-checkbox").on("input", function() {
        handle_bills();
    });
})
