function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

function update_budget_history(){
    console.log("Updating budget history")
    const csrftoken = getCookie("csrftoken");

    $.ajaxSetup({
        headers: {
            "X-CSRFToken": csrftoken
        }
    });

    $.ajax({
        url: "/budget",
        method: "POST",
        data: {
            "type": "update_budget_history"
        },
        success: function(response){
            console.log("SUCCESS")
        },
        error: function(xhr, status, error){
            console.log(xhr)
        }
    });
}

function update_monthly_budget(){
    console.log("Updating Monthly Budget")
    const csrftoken = getCookie("csrftoken");

    toggle_update_budget_loader();

    $.ajaxSetup({
        headers: {
            "X-CSRFToken": csrftoken
        }
    });

    $.ajax({
        url: "/budget",
        method: "POST",
        data: {
            "type": "update_monthly_budget"
        },
        success: function(response){
            console.log("SUCCESS")
            toggle_update_budget_loader();
            toggle_update_budget_success();
        },
        error: function(xhr, status, error){
            console.log(xhr)
        }
    });
}