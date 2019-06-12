function CargaColoring(){
  $("td[class*='delay_checker']").each(function () {

    var value = $(this).html();

    if (value == 1) {
      $(this).css("background-color","green");
      $(this).css("color","green");

    } else {
      $(this).css("background-color","white");
      $(this).css("color","white");
    }

  })

}
