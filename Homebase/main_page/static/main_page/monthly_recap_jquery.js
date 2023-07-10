function navbarHandler(){
    // get checked item in navbar
    const clickedElement = $(this)

    if (clickedElement.attr("data-checked") == "false"){
        const currently_checked_elemenet = $('.monthly-recap-navbar-item[data-checked="true"]')
        const currently_shown_page_id = currently_checked_elemenet.attr("linked-page")

        $("#" + currently_shown_page_id).hide()
        // set all other items to false
        $(".monthly-recap-navbar-item").map(function() {
            $(this).attr("data-checked", "false")
        })

        clickedElement.attr("data-checked", "true")
        const clicked_element_page_id = $(this).attr("linked-page")
        $("#" + clicked_element_page_id).attr("style", "display:flex;")
        console.log(clicked_element_page_id)
    }
}

function colorCodeNumbers(){
    console.log("Color Coding Values")

    $(".color-number").map(function() {
        var number = this.innerHTML
        var cleaned_number = Number(number.replace("%", "").replace("€", ""))

        if (cleaned_number > 0){
            $(this).addClass("positive-number")
        } else if (cleaned_number < 0){
            $(this).addClass("negative-number")
        }
    })
}

$(document).ready(function(){
    colorCodeNumbers()

    $(".monthly-recap-navbar-item").click(function() {
        navbarHandler.call(this);
    })
})
