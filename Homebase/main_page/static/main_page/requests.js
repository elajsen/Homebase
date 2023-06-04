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

function get_budget(){
    console.log("Getting budget history")
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
            "type": "update_budget"
        },
        success: function(response){
            console.log("SUCCESS")
        },
        error: function(xhr, status, error){
            console.log(xhr)
        }
    });
}