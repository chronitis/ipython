define(["widgets/js/widget"], function(WidgetManager) {

    var MPLDropdownView = IPython.DOMWidgetView.extend({
        render : function(){
            // Called when view is rendered.
            this.$el
                .addClass('widget-hbox-single');
            this.$label = $('<div />')
                .appendTo(this.$el)
                .addClass('widget-hlabel')
                .hide();
            this.$buttongroup = $('<div />')
                .addClass('widget_item')
                .addClass('btn-group')
                .appendTo(this.$el);
            this.$el_to_style = this.$buttongroup; // Set default element to style
            this.$droplabel = $('<button />')
                .addClass('btn btn-default')
                .addClass('widget-combo-btn')
                .html("&nbsp;")
                .appendTo(this.$buttongroup);
            this.$dropbutton = $('<button />')
                .addClass('btn btn-default')
                .addClass('dropdown-toggle')
                .addClass('widget-combo-carrot-btn')
                .attr('data-toggle', 'dropdown')
                .append($('<span />').addClass("caret"))
                .appendTo(this.$buttongroup);
            this.$droplist = $('<ul />')
                .addClass('dropdown-menu')
                .appendTo(this.$buttongroup);

            // Set defaults.
            this.update();
        },

        update : function(options){
            // Update the contents of this view
            //
            // Called when the model is changed.  The model may have been
            // changed by another view or by a state update from the back-end.

            if (options === undefined || options.updated_view != this) {
                var selected_item = this.model.get('value');
                var codes = this.model.get('codes');
                var svg = this.model.get('svg');
                this.$droplabel.html(svg[codes.indexOf(selected_item)]); //.html(""+ selected_item + items[selected_item]);

                if (this.model.get("mpl-type") == "cmap") {

                }
                var $replace_droplist = $('<ul />')
                    .addClass('dropdown-menu');
                var that = this;
                _.each(codes, function(code, i) {
                    var item_button = $('<a href="#"/>')
                        .html(svg[i]) //.html(""+key+svg)
                        .attr('key', code)
                        .on('click', $.proxy(that.handle_click, that));
                    $replace_droplist.append($('<li />').css('float', 'left').append(item_button));
                });

                this.$droplist.replaceWith($replace_droplist);
                this.$droplist.remove();
                this.$droplist = $replace_droplist;

                if (this.model.get('disabled')) {
                    this.$buttongroup.attr('disabled','disabled');
                    this.$droplabel.attr('disabled','disabled');
                    this.$dropbutton.attr('disabled','disabled');
                    this.$droplist.attr('disabled','disabled');
                } else {
                    this.$buttongroup.removeAttr('disabled');
                    this.$droplabel.removeAttr('disabled');
                    this.$dropbutton.removeAttr('disabled');
                    this.$droplist.removeAttr('disabled');
                }

                var description = this.model.get('description');
                if (description.length === 0) {
                    this.$label.hide();
                } else {
                    this.$label.text(description);
                    MathJax.Hub.Queue(["Typeset",MathJax.Hub,this.$label.get(0)]);
                    this.$label.show();
                }
            }
            return MPLDropdownView.__super__.update.apply(this);
        },

        handle_click: function (e) {
            // Handle when a value is clicked.

            // Calling model.set will trigger all of the other views of the
            // model to update.
            var obj = e.target;
            while (!$(obj).is("[key]")) obj = $(obj).parent();
            this.model.set('value', $(obj).attr('key'), {updated_view: this});
            this.touch();
        },

    });
    WidgetManager.register_widget_view('MPLDropdownView', MPLDropdownView);
});
