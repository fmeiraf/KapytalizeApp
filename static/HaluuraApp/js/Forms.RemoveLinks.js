// Delete forms and instances funcionalities

!(function($){

  $.fn.RemoveLinks = function (opts) {

    var options = $.extend({}, $.fn.RemoveLinks.defaults, opts),
        totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
        maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
        minForms = $('#id_' + options.prefix + '-MIN_NUM_FORMS'),
        childElementSelector = 'input,select,textarea,label,div',
        containerId = $('#' + options.containerId),
        $$ = $(this),

        hasChildElements = function(row) {
            return row.find(childElementSelector).length > 0;
        },

        // Update Element indexes after deletions
        updateElementIndex = function(elem, prefix, ndx) {
            var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                replacement = prefix + '-' + ndx + '-';
            if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
            if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
            if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
        },
        // check if we are in a situação where there no instance to show buttons for
        showDeleteLinks = function() {
          return minForms.val() == '' ||
                (totalForms.val() - minForms.val() > 0);
        },

        //encapsulating the remove link additions and functions
        insertDeleteLink = function (row) {
          var delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, '.'),
              linkAlreadExist = row.find('a.' + options.deleteCssClass );

          if (!linkAlreadExist.length) {

              if (row.is('TR')) {
                  // If the forms are laid out in table rows, insert
                  // the remove button into the last table cell:
                  row.children(':last').append('<a class="' + options.deleteCssClass +'" href="javascript:void(0)">' + options.deleteText + '</a>');
              } else if (row.is('UL') || row.is('OL')) {
                  // If they're laid out as an ordered/unordered list,
                  // insert an <li> after the last list item:
                  row.append('<li><a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a></li>');
              } else {
                  // Otherwise, just insert the remove button as the
                  // last child element of the form's container:
                  row.append('<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a>');
              }
          }
              // Check if we're under the minimum number of forms - not to display delete link at rendering
         if (!showDeleteLinks()){
              row.find('a.' + delCssSelector).hide();
          }

          row.find('a.' + delCssSelector).click(function() {
              var row = $(this).parents("div#form-block"),
                  del = row.find('input:hidden[id $= "-DELETE"]'),
                  forms = '';

              if (del.length) {

                del.val('on');
                row.hide();
                forms = row.not(':hidden');

              } else {
                row.hide();
                // Update the TOTAL_FORMS count:
                forms = row.not(':hidden');
                totalForms.val(forms.length);
              }
            for (var i=0, formCount=forms.length; i<formCount; i++) {
                if (!del.length) {
                  // Also update names and IDs for all child controls (if this isn't
                  // a delete-able inline formset) so they remain in sequence:
                  console.log('I am on updateElementIndex');
                  forms.eq(i).find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, i);
                  });
                }
          }
        });

      };


    $$.each(function(i){
      var row = $(this),
          del = row.find('input:checkbox[id $= "-DELETE"]');
      // console.log('here');
      if (del.length) {
            // If you specify "can_delete = True" when creating an inline formset,
            // Django adds a checkbox to each form in the formset.
            // Replace the default checkbox with a hidden field:
          if (del.is(':checked')) {
                // If an inline formset containing deleted forms fails validation, make sure
                // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
              del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" value="on" />');
              row.hide();
          } else {
              del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
          }
            // Hide any labels associated with the DELETE checkbox:
          $('label[for="' + del.attr('id') + '"]').hide();
          del.remove();
      }

      if (hasChildElements(row)) {
            // row.addClass(options.formCssClass);
        if (row.is(':visible')) {
              insertDeleteLink(row);
        }
      }
      return $$;
      });
  };

  $.fn.RemoveLinks.defaults = {
    deleteText: 'Excluir Ativo',            // Text for the delete link
    addCssClass: 'add-row',          // CSS class applied to the add link
    deleteCssClass: 'delete-row btn btn-danger btn-sm',
    containerId: null
  };

})(jQuery);
