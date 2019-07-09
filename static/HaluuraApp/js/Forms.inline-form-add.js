/*
  django-inline-formset.js

  @author Benjamin W Stookey

  https://github.com/jamstooks/jquery-django-inline-form
*/
!function($) {

  $.fn.djangoInlineFormAdd = function(opts) {

    if(opts.prefix != undefined) {
      this.prefix = opts.prefix;
      this.containerId = '#' + this.prefix + '-container';
      this.templateId = '#' + this.prefix + '-template';
      this.totalFormsId = '#id_' + this.prefix + '-TOTAL_FORMS';
      this.maxFormsId = '#id_' + this.prefix + '-MAX_NUM_FORMS';
      this.minFormsId = '#id_' + this.prefix + '-MIN_NUM_FORMS';
      this.deleteButtonClass = 'delete-block';
      this.deleteText = 'Excluir';
      this.childElementSelector = 'input,select,textarea,label,div,span';

      this.deleteButtonId = '#' + this.prefix + '-delete';
    }
    else {
      if( opts.containerId == undefined ||
          opts.templateId == undefined ||
          opts.totalFormsId == undefined ||
          opts.maxFormsId == undefined ||
          opts.minFormsId == undefined
      ){
        console.error("[djangoInlineForm] if prefix is not provided in opts, containerId, templateId, totalFormsId, and maxFormsId must be");
        return;
      }
    }
    // even if a prefix is defined, ids may change
    this.containerId = opts.containerId != undefined ? opts.containerId : this.containerId;
    this.templateId = opts.templateId != undefined ? opts.templateId : this.templateId;
    this.totalFormsId = opts.totalFormsId != undefined ? opts.totalFormsId : this.totalFormsId;
    this.maxFormsId = opts.maxFormsId != undefined ? opts.maxFormsId : this.maxFormsId;
    this.minFormsId = opts.minFormsId != undefined ? opts.minFormsId : this.minFormsId;

    this.deleteButtonId = opts.deleteButtonId != undefined ? opts.deleteButtonId : this.deleteButtonId;

    this.postClick = opts.postClick != undefined ? opts.postClick : null;
    this.formHeight = opts.formHeight != undefined ? opts.formHeight : null;

    var max = $(this.maxFormsId).attr('value');

    var self = this;

    this.addForm = function(ev) {
      ev.preventDefault();
      // var count = $(self.containerId).children().length;
      var count = $('.manage-form-frame').length - 2;
      if (count >= max) {
        console.log('exceeded max inline forms');  // should maybe have a callback option
        return;
      }
      console.log
      var tmplMarkup = $(self.templateId).html();
      var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
      // $(self.containerId).append(compiledTmpl);
      $('#lastFormFake').before(compiledTmpl);

      // run postClick method
      if (self.postClick != null) { self.postClick(); }

      // animate it
      $(self.containerId).children().last().show('slow');

      // update form count
      $(self.totalFormsId).attr('value', count+1);

      // some animate to scroll to view our new form
      if(self.formHeight != null) {
        $('html, body').animate({
          scrollTop: $(window).scrollTop() + self.formHeight
        }, 800);
      }
    };

    this.removeForm = function(ev) {
      $(self.containerId).children().last().hide('slow', function(){
        $(self.containerId).children().last().remove();
        $(self.totalFormsId).attr('value', $(self.containerId).children().length);
      });
      // some animate to scroll up
      if(self.formHeight != null) {
        $('html, body').animate({
          scrollTop: $(window).scrollTop() - self.formHeight
        }, 800);
      }
    }

    this.click(this.addForm);
    if(this.deleteButtonId != null) {
      $(this.deleteButtonId).click(this.removeForm);
    }
  }
}(window.jQuery);
