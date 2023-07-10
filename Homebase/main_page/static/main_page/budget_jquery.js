function check_last_update(){
    function get_current_date(){
        const current_date = new Date().toJSON().replace("T", " ").replace("Z", "")
        return current_date
    }

    const current_date_str = get_current_date().split(".")[0]

    const last_update_date_str = $("#last_update_date").html().split(": ")[1]
    
    const last_update_date = new Date(last_update_date_str)
    const current_date = new Date(current_date_str)

    if (current_date > last_update_date){
        const link = $("#update-button a")
        link.click()
    }
}

function update_amounts(){
    const total_spending = $("#budget-modal-section").attr("total_spending")
    const salary = $("#budget_salary").val()
    const savings = $("#budget_savings").val()

    const total_bills = $("#bills").attr("total_bills")

    console.log("total_spending", total_spending)
    console.log("salary", salary)
    console.log("savings", savings)
    console.log("total bills", total_bills)

    const new_net = Number((salary - total_spending - savings - total_bills).toFixed(2))

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

    if (!value){
        bill_amounts = 0
    }

    $("#bills").attr("total_bills", bill_amounts.toFixed(2))
    update_amounts()
}

function update_total_spending(){
    let new_total_amount = 0

    $(".spending-amount").map(function() {
        const number_string = $(this).html().replace("€", "")
        console.log("Spending")
        console.log(number_string)
        new_total_amount += Number(number_string)
    })

    $(".income-amount").map(function() {
        const number_string = $(this).html().replace("€", "")
        console.log("Income")
        console.log(number_string)
        new_total_amount -= Number(number_string)
    })
    console.log("Total")
    console.log(new_total_amount)
    $("#budget-modal-section").attr("total_spending", new_total_amount)
}

function handle_last_month_bills(){
    console.log("running function")

    const is_checked = $("#last-month-bills-checkbox").is(":checked");
    const type = $("#last_month_spending").attr("type")

    if (is_checked){
        const last_month_bill_amount = $("#last_month_spending").html()
        const current_month_bill_amount = $('[title="Hogar"]').next().html()

        $("#last_month_spending").html(current_month_bill_amount)
        $("#last_month_spending").attr("type", "current_month_bill_amounts")
        $('[title="Hogar"]').next().html(last_month_bill_amount)

    } else {
        const last_month_bill_amount = $('[title="Hogar"]').next().html()
        const current_month_bill_amount = $("#last_month_spending").html()
        
        $("#last_month_spending").html(last_month_bill_amount)
        $("#last_month_spending").attr("type", "last_month_bill_amounts")
        $('[title="Hogar"]').next().html(current_month_bill_amount)
    }

    update_total_spending();
    update_amounts();
}

$(document).ready(function(){
    check_last_update()
    handle_bills()
    handle_last_month_bills()

    $("#budget_savings").on("input", function() {
        update_amounts();
    });
    $("#budget_salary").on("input", function() {
        update_amounts();
    });
    $("#budget-remove-checkbox").on("input", function() {
        handle_bills();
    });
    $("#last-month-bills-checkbox").on("input", function(){
        handle_last_month_bills();
    })
})
