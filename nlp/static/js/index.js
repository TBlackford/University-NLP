$.get("/api/universities", function(data) {

    var content = "";

    var unis = data.universities;

    for(var i = 0; i < unis.length; i++) {

        content += "<option value='" + unis[i].rank + "'>" + unis[i].name + "</option>"

    }

    $(".uni_list").append(content);

});