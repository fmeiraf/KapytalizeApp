!(function DisplayCorrectFields ($) {
  $.fn.DisplayCorrectFields = function () {
    $(this).each(function(){
      // console.log($(this));
      var tipoAtivo = $(this).find("select[id*='tipo_ativo']").val(),
          taxa_container = $(this).find("input[id*='taxa_entrada']").parent(),
          taxa_status_hidden = taxa_container.is(':hidden');

      if (tipoAtivo == 3) {
          if (taxa_status_hidden) {
            taxa_container.show();
            AutoFilterForm();
          }
      } else {
          if (!taxa_status_hidden) {
            taxa_container.hide();
            AutoFilterForm();
          }
      }

    })
  }
})(jQuery);
