$(document).ready(function(){

    var search_query = {
        state: null,
        felony: false,
        misdemeanor: false,
        offenses: [],
        query_url: null,
        get_state: function(){
            var options = $("option");
            for (var i=0; i < options.length; i++) {
                if (options[i].selected) {
                    this.state = options[i].value;
                    break;
                }
            }
        },
        get_offenses: function(){
            var offenses = $("#offenses .secondary"),
                to_apply = [];
            for (var i=0; i < offenses.length; i++) {
                to_apply.push(offenses[i].value);
            }
            this.offenses = to_apply;
        },
        build_query: function(){
            var output = '/results/',
                paste = '&';

            output += this.state + "/?";
            if (this.felony) {
                output += "felony=True" + paste;
            }
            if (this.misdemeanor) {
                output += "misdem=True" + paste;
            }
            if (this.offenses) {
                for (var i=0; i < this.offenses.length; i++) {
                    output += "offense=" + this.offenses[i];
                    if (i < this.offenses.length - 1) {
                        output += paste;
                    }
                }
            }
            this.query_url = output;
            window.location = this.query_url;
        },
    }

    var state_form = $("#state-form");
    state_form.submit(function(e){
        e.preventDefault();
        search_query.get_state();
    });

    var felony_bool = $("#felony button");
    felony_bool.click(function(){
        var item = $(this);
        felony_bool.addClass("info");
        item.removeClass("info");
        search_query.felony = eval(item[0].value);
    });

    var misdem_bool = $("#misdem button");
    misdem_bool.click(function(){
        var item = $(this);
        misdem_bool.addClass("info");
        item.removeClass("info");
        search_query.misdemeanor = eval(item[0].value);
    });

    var offenses = $("#offenses button");
    offenses.click(function(){
        var item = $(this);
        if (item.hasClass("secondary")) {
            item.removeClass("secondary");
        } else {
            item.addClass("secondary");
        }
    });

    var submit = $("#submit-request");
    submit.click(function(){
        search_query.get_offenses();
        search_query.build_query();
    });
});