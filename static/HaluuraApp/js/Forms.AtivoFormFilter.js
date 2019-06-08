function AutoFilterForm(){
  $("select[id*='tipo_ativo']").change(function () {
        // dealing with filtering the form fields automaticaly
        var url = $("#AplicacaoCreateForm").attr("data-ativo-url"),  // get the url of the `tipo_ativo` view
            tipoAtivo = $(this).val(),  // get the selected ativo ID from the HTML input
            id = $(this).attr('id'),
            id_number = id.replace( /\D/g, ''),
            id_campo_taxa = id.replace('tipo_ativo', 'taxa_entrada'),
            taxa_container = $('#' + id_campo_taxa).parent(),
            taxa_status_hidden = taxa_container.is(':hidden');



        // $.ajax({                       // initialize an AJAX request
        //   url: url,                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
        //   data: {
        //     'tipo_ativo': tipoAtivo       // add the tipo_ativo id to the GET parameters
        //   },
        //   success: function (data) {   // `data` is the return of the `ativo_formfilter` view function
        //     $("select[id*='"+id_number+"-ativo']").html(data);  // replace the contents of the tipo_ativo input with the data that came from the server
        //   }
        // })

        // hiding unecessary fields for certain types of assets

        if (tipoAtivo == 3) {
            if (taxa_status_hidden) {
              taxa_container.show();
            }
        } else {
            if (!taxa_status_hidden) {
              taxa_container.hide();
            }
        }
    }
  )};
