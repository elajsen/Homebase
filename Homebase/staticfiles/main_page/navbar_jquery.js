function handle_navabar_modal(element){
    console.log("Toggle Modal")
    $("#navbar_modal").toggle()

    const position = $(element).position()
    const top = position["top"]
    const item_height = $(element).height()

    const width = $("#top_bar").width()
    const modal_height = $("#navbar_modal").height()

    $("#navbar_modal").css("top", top - (modal_height / 2) + (item_height / 2));
    $("#navbar_modal").css("left", width);
}

$(document).ready(function(){
    $(".top_bar_item").hover(function() {
        console.log($("#navbar_modal").css("display"))
        if ($("#navbar_modal").css("display") != "flex"){
            handle_navabar_modal(this);
        } 
    })

    $("#navbar_modal").mouseleave(function() {
        if ($("#navbar_modal").css("display") == "flex"){
            $("#navbar_modal").toggle()
        }
    })
})
