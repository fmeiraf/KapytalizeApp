!(function DisplayCorrectFields ($) {
  $.fn.DisplayCorrectFields = function () {
    $(this).each(function(){
      // console.log($(this));
      var tipoAtivo = $(this).find("select[id*='tipo_ativo']").val(),
          taxa_container = $(this).find("input[id*='taxa_entrada']").parent(),
          taxa_label = $(this).find("label[for*='taxa_entrada']"),
          taxa_status_hidden = taxa_container.is(':hidden'),
          preco_container = $(this).find("input[id*='preco_entrada']").parent(),
          preco_field = $(this).find("input[id*='preco_entrada']"),
          preco_status_hidden = preco_container.is(':hidden');

      if (tipoAtivo == 3) {
        if (taxa_status_hidden) {
          taxa_container.show();
        }
        if (preco_status_hidden) {
          preco_container.show();
        }
      } else if ((tipoAtivo == 4) || (tipoAtivo == 5)) {
        taxa_label.text('% do CDI');
        if (taxa_status_hidden) {
          taxa_container.show();
        }
        if (preco_status_hidden) {
          preco_field.val(1);
        } else {
          preco_field.val(1);
          preco_container.hide();
        }
      }else {
        if (!taxa_status_hidden) {
          taxa_container.hide();
        }
        if (preco_status_hidden) {
          preco_container.show();
        }
      }

      $(this).find("select[id*='tipo_ativo']").change(function() {

        var tipoAtivo = $(this).val(),
            parent_form = $(this).parents()[1],
            taxa_container = $(parent_form).find("input[id*='taxa_entrada']").parent(),
            taxa_label = $(parent_form).find("label[for*='taxa_entrada']"),
            taxa_status_hidden = taxa_container.is(':hidden'),
            preco_container = $(parent_form).find("input[id*='preco_entrada']").parent(),
            preco_field = $(parent_form).find("input[id*='preco_entrada']"),
            preco_status_hidden = preco_container.is(':hidden');

        console.log(tipoAtivo);
        console.log(taxa_label);

        if (tipoAtivo == 3) {
          if (taxa_status_hidden) {
            taxa_label.text('Taxa pré-fixada / % do CDI %');
            taxa_container.show();
          }
          if (preco_status_hidden) {
            preco_container.show();
          }
        }
        else if ((tipoAtivo == 4) || (tipoAtivo == 5)) {
          if (taxa_status_hidden) {
            taxa_label.text('Taxa pré-fixada / % do CDI %');
            taxa_container.show();
          }
          if (preco_status_hidden) {
            preco_field.val(1);
          }
          else {
            preco_field.val(1);
            preco_container.hide();
          }
        }
        else {
          console.log('aqui');
          if (!taxa_status_hidden) {
            taxa_container.hide();
          }
          if (preco_status_hidden) {
            preco_container.show();
          }
        }


      })



  })
}
})(jQuery);
